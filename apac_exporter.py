import os
import pandas as pd
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
from sqlalchemy import text
import logging

from api.logging import log_export_event, setup_logging

# Importa a classe de conexão e o mapeamento do módulo compartilhado
from shared.database import Database
from shared.mapeamento_procedimentos import carregar_tabela_procedimentos_cid

setup_logging()
logger = logging.getLogger("exporter.apac")

class APACExporter:
    """
    Classe responsável pela lógica de negócio da exportação de arquivos APAC.
    """
    def __init__(self):
        self.conn = None
        self.gui_log_callback = None
        self.config = {
            'orgao_responsavel': 'APAE DE COLINAS DO TOCANTINS',
            'sigla_orgao': 'APAE',
            'cgc_cpf': '25062282000182',
            'orgao_destino': 'SECRETARIA MUNICIPAL DE SAUDE',
            'indicador_destino': 'M',
            'versao_sistema': 'V04.10-APAC',
            'cnes': '2560372'
        }

    def _log_message_gui(self, message):
        if self.gui_log_callback and callable(self.gui_log_callback):
            self.gui_log_callback(message)
        logger.info(message, extra={"event": "export_message"})
    
    def carregar_mapeamento_procedimentos(self, cod_procs_bd_unicos):
        """Carrega o mapeamento de 'cod_proc' (ID) para 'codigo_procedimento' (código curto)."""
        mapeamento_proc = {}
        if not self.conn or not cod_procs_bd_unicos: return mapeamento_proc
        try:
            from sqlalchemy import table, column, select
            procedimentos_table = table("procedimentos", column("id_procedimento"), column("codigo_procedimento"), schema="sigh")
            cod_procs_list = [str(c) for c in cod_procs_bd_unicos if c]
            if not cod_procs_list: return mapeamento_proc
            query = select(procedimentos_table.c.id_procedimento, procedimentos_table.c.codigo_procedimento)\
                .where(procedimentos_table.c.id_procedimento.in_(cod_procs_list))
            result = self.conn.execute(query)
            for row in result: 
                mapeamento_proc[str(row.id_procedimento)] = str(row.codigo_procedimento)
        except Exception as e:
            print(f"Erro ao carregar mapeamento de procedimentos: {str(e)}")
        return mapeamento_proc

    def _build_sql_apac(self, data_inicio, data_fim):
        """Query completa e robusta (baseada no bpa_exporter) para buscar todos os dados necessários."""
        data_inicio_str = data_inicio.isoformat()
        data_fim_str = data_fim.isoformat()
        return f"""
        WITH RankedEnderecos AS (
            SELECT
                ep.cod_paciente, ep.cod_logradouro, ep.numero,
                ROW_NUMBER() OVER(PARTITION BY ep.cod_paciente ORDER BY ep.data_hora_atualizacao DESC, ep.data_hora_criacao DESC, ep.id_endereco DESC) as rn
            FROM sigh.enderecos ep
            WHERE ep.ativo = 't' AND ep.cod_logradouro IS NOT NULL
        )
        SELECT
            p.id_paciente, p.nm_paciente, v_pac.mae AS nm_mae, p.data_nasc, p.cod_sexo,
            v_pac.cartao_sus AS cns_paciente, p.cod_raca_etnia, p.cod_etnia_indigena, p.cod_nacionalidade,
            CASE
                WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.data_nasc)) < 18 THEN v_pac.mae
                ELSE p.nm_paciente
            END AS nome_responsavel_paciente,
            logradouros_pac.logradouro, enderecos_pac.numero AS numero_endereco,
            logradouros_pac.bairro_inicial AS bairro, logradouros_pac.cep,
            aihu_cep_ibge.ibge AS ibge_municipio_paciente,
            prestador_lanc.nm_prestador AS nm_medico_responsavel,
            prestador_lanc.cns AS cns_medico_responsavel,
            l.id_lancamento, l.cod_proc, l.quantidade, l.data AS data_atendimento_procedimento,
            vcpc.codigo_cbo, fi.diagnostico AS cid_principal_procedimento, l.cod_serv AS cod_servico
        FROM
            sigh.lancamentos l
        JOIN sigh.contas c ON l.cod_conta = c.id_conta
        JOIN sigh.ficha_amb_int fi ON c.cod_fia = fi.id_fia
        JOIN sigh.pacientes p ON fi.cod_paciente = p.id_paciente
        LEFT JOIN sigh.v_cons_pacientes_laboratorios v_pac ON p.id_paciente = v_pac.registro
        LEFT JOIN sigh.v_cons_prestadores_cbos_scola vcpc ON l.cod_prestador = vcpc.id_prestador
        LEFT JOIN sigh.prestadores prestador_lanc ON l.cod_prestador = prestador_lanc.id_prestador
        LEFT JOIN RankedEnderecos AS enderecos_pac ON p.id_paciente = enderecos_pac.cod_paciente AND enderecos_pac.rn = 1
        LEFT JOIN endereco_sigh.logradouros AS logradouros_pac ON enderecos_pac.cod_logradouro = logradouros_pac.id_logradouro
        LEFT JOIN aihu.ceps_municipios_ibges AS aihu_cep_ibge ON logradouros_pac.cep = aihu_cep_ibge.cep
        WHERE
            l.data BETWEEN '{data_inicio_str}' AND '{data_fim_str}'
        ORDER BY
            p.id_paciente, l.data;
        """

    def deduplicate_por_id_lancamento_original(self, registros_filtrados):
        """Deduplica mantendo apenas um registro por 'id_lancamento' único."""
        self._log_message_gui(f"Iniciando deduplicação de {len(registros_filtrados)} registros...")
        if not registros_filtrados: return []
        ids_vistos = set()
        registros_finais = []
        for registro in registros_filtrados:
            id_original = registro.get('id_lancamento')
            if id_original is not None and id_original not in ids_vistos:
                ids_vistos.add(id_original)
                registros_finais.append(registro)
        self._log_message_gui(f"Deduplicação concluída: {len(registros_finais)} registros únicos restantes.")
        return registros_finais

    def processar_e_gerar_apac(self, params_execucao):
        """Orquestra a busca, FILTRAGEM, processamento e geração do arquivo APAC."""
        if not self.conn: return False, "Sem conexão com o banco."
        try:
            self._log_message_gui("Iniciando consulta de dados...")
            log_export_event(logger, "consulta_apac_inicio", status="started")
            sql = self._build_sql_apac(params_execucao['data_inicio'], params_execucao['data_fim'])
            result = self.conn.execute(text(sql))
            registros_brutos = [dict(row._mapping) for row in result.fetchall()]
            self._log_message_gui(f"{len(registros_brutos)} lançamentos brutos encontrados no período.")

            if not registros_brutos:
                return False, "Nenhum lançamento encontrado para o período."

            self._log_message_gui("Filtrando e validando procedimentos de APAC...")
            tabela_proc_cid = carregar_tabela_procedimentos_cid()
            cod_procs_unicos = {reg.get('cod_proc') for reg in registros_brutos if reg.get('cod_proc')}
            mapeamento_curto = self.carregar_mapeamento_procedimentos(cod_procs_unicos)

            registros_apac_filtrados = []
            erros_mapeamento = set()

            for reg in registros_brutos:
                cod_proc = reg.get('cod_proc')
                if not cod_proc: continue
                
                codigo_curto = mapeamento_curto.get(str(cod_proc))
                if not codigo_curto:
                    erros_mapeamento.add(f"ID de Proc. {cod_proc} não possui 'código curto' em sigh.procedimentos.")
                    continue

                proc_info = tabela_proc_cid.get(codigo_curto)
                if not proc_info:
                    erros_mapeamento.add(f"Código curto '{codigo_curto}' (ID {cod_proc}) não está em shared/mapeamento_procedimentos.py.")
                    continue
                
                if proc_info.get('categoria') == 'APAC':
                    reg['proc_info'] = proc_info
                    registros_apac_filtrados.append(reg)
            
            if erros_mapeamento:
                self._log_message_gui(f"AVISO: {len(erros_mapeamento)} tipos de procedimentos ignorados por falha no mapeamento.")
                for erro in list(erros_mapeamento)[:5]: self._log_message_gui(f"  - {erro}")

            self._log_message_gui(f"Filtragem concluída: {len(registros_apac_filtrados)} lançamentos de APAC encontrados.")
            if not registros_apac_filtrados:
                return False, "Nenhum procedimento de APAC encontrado (após o filtro)."

            registros_apac_deduplicados = self.deduplicate_por_id_lancamento_original(registros_apac_filtrados)
            log_export_event(
                logger,
                "apac_filtrados",
                batch_size=len(registros_apac_deduplicados),
                status="ok",
            )

            self._log_message_gui("Agrupando procedimentos por paciente...")
            pacientes_com_procedimentos = {}
            for reg in registros_apac_deduplicados:
                id_paciente = reg['id_paciente']
                if id_paciente not in pacientes_com_procedimentos:
                    pacientes_com_procedimentos[id_paciente] = {'dados_paciente': reg, 'procedimentos': []}
                pacientes_com_procedimentos[id_paciente]['procedimentos'].append(reg)
            self._log_message_gui(f"{len(pacientes_com_procedimentos)} pacientes únicos para gerar APACs.")

            self._log_message_gui("Gerando arquivo APAC formatado...")
            sucesso, resultado = self.gerar_arquivo_apac_formatado(pacientes_com_procedimentos, params_execucao)
            log_export_event(
                logger,
                "arquivo_apac",
                batch_size=len(pacientes_com_procedimentos),
                status="success" if sucesso else "error",
                caminho=params_execucao.get('caminho_arquivo'),
            )
            return sucesso, resultado

        except Exception as e:
            error_msg = f"Erro fatal ao processar e gerar APAC: {e}"
            logger.exception(error_msg, extra={"event": "export_error"})
            self._log_message_gui(error_msg)
            return False, str(e)

    def gerar_arquivo_apac_formatado(self, pacientes_dados, params):
        """Gera o arquivo TXT formatado da APAC com múltiplos tipos de registro."""
        def formatar(valor, tamanho, tipo='char', pad_char=' '):
            valor_str = str(valor or '').strip()
            if tipo == 'num':
                return ''.join(filter(str.isdigit, valor_str)).zfill(tamanho)[:tamanho]
            else:
                return valor_str.ljust(tamanho, pad_char)[:tamanho]
        
        numero_apac_atual = int(params['numero_inicial'])
        data_inicio_validade = params['data_inicio_validade']
        data_fim_validade = data_inicio_validade + datetime.timedelta(days=90)
        
        with open(params['caminho_arquivo'], 'w', encoding='latin-1', newline='') as f:
            header = "".join([
                formatar('01', 2, 'num'), formatar('#APAC', 5), formatar(params['competencia'], 6, 'num'),
                formatar(len(pacientes_dados), 6, 'num'), formatar('1111', 4, 'num'),
                formatar(self.config.get('orgao_responsavel'), 30), formatar(self.config.get('sigla_orgao'), 6),
                formatar(self.config.get('cgc_cpf'), 14, 'num'), formatar(self.config.get('orgao_destino'), 40),
                formatar(self.config.get('indicador_destino'), 1), formatar(datetime.datetime.now().strftime('%Y%m%d'), 8, 'num'),
                formatar(self.config.get('versao_sistema'), 15),
            ]).ljust(137)
            f.write(header + '\r\n')

            for id_paciente, dados_paciente in pacientes_dados.items():
                principal = dados_paciente['dados_paciente']
                proc_principal_info = dados_paciente['procedimentos'][0]['proc_info']
                proc_principal_sigtap = proc_principal_info.get('codigo_sigtap', '0000000000')
                num_apac_com_dv = str(numero_apac_atual).zfill(12) + '1'

                corpo_str = "".join([
                    formatar('14', 2, 'num'), formatar(params['competencia'], 6, 'num'),
                    formatar(num_apac_com_dv, 13, 'num'), formatar('27', 2, 'num'), # UF
                    formatar(self.config.get('cnes'), 7, 'num'), formatar(datetime.datetime.now().strftime('%Y%m%d'), 8, 'num'),
                    formatar(data_inicio_validade.strftime('%Y%m%d'), 8, 'num'), formatar(data_fim_validade.strftime('%Y%m%d'), 8, 'num'),
                    formatar('01', 2, 'num'), formatar('1', 1, 'num'),
                    formatar(principal.get('nm_paciente'), 30), formatar(principal.get('nm_mae'), 30),
                    formatar(principal.get('logradouro'), 30), formatar(principal.get('numero_endereco'), 5),
                    formatar('', 10), formatar(principal.get('cep'), 8, 'num'),
                    formatar(principal.get('ibge_municipio_paciente'), 7, 'num'),
                    formatar(principal.get('data_nasc').strftime('%Y%m%d') if principal.get('data_nasc') else '', 8, 'num'),
                    formatar('M' if str(principal.get('cod_sexo')) == '1' else 'F', 1),
                    formatar(principal.get('nm_medico_responsavel'), 30),
                    formatar(proc_principal_sigtap, 10, 'num'),
                    formatar('01', 2, 'num'), formatar('', 8),
                    formatar(principal.get('nm_medico_responsavel'), 30), # Nome Autorizador
                    formatar(principal.get('cns_paciente'), 15, 'num'),
                    formatar(principal.get('cns_medico_responsavel'), 15, 'num'),
                    formatar(principal.get('cns_medico_responsavel'), 15, 'num'), # CNS Autorizador
                    formatar('', 4), formatar('', 10), formatar('', 7),
                    formatar(data_inicio_validade.strftime('%Y%m%d'), 8, 'num'),
                    formatar(data_inicio_validade.strftime('%Y%m%d'), 8, 'num'),
                    formatar('010101', 10), formatar('01', 2, 'num'), formatar('', 13),
                    formatar(principal.get('cod_raca_etnia'), 2, 'num'),
                    formatar(principal.get('nome_responsavel_paciente'), 30),
                    formatar(principal.get('cod_nacionalidade'), 3, 'num'),
                    formatar(principal.get('cod_etnia_indigena'), 4, 'num'),
                    formatar('', 3), formatar(principal.get('bairro'), 30),
                    formatar('', 2), formatar('', 9), formatar('', 40),
                    formatar(principal.get('cns_medico_responsavel'), 15, 'num'), # CNS Executante
                    formatar('', 11), formatar('', 10), formatar('N', 1),
                ]).ljust(533)
                f.write(corpo_str + '\r\n')

                for proc in dados_paciente['procedimentos']:
                    proc_info = proc['proc_info']
                    linha_proc_str = "".join([
                        formatar('13', 2, 'num'), formatar(params['competencia'], 6, 'num'),
                        formatar(num_apac_com_dv, 13, 'num'), formatar(proc_info.get('codigo_sigtap'), 10, 'num'),
                        formatar(proc.get('codigo_cbo'), 6, 'num'), formatar(proc.get('quantidade'), 7, 'num'),
                        formatar('', 14), formatar('', 6),
                        formatar(proc.get('cid_principal_procedimento'), 4), formatar('', 4),
                        formatar(proc_info.get('servico'), 3, 'num'),
                        formatar(proc_info.get('classificacao'), 3, 'num'),
                        formatar('', 8), formatar('', 4), formatar('', 7),
                    ]).ljust(97)
                    f.write(linha_proc_str + '\r\n')
                
                numero_apac_atual += 1

        return True, params['caminho_arquivo']

class APACExporterGUI:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Exportador APAC (SIGH)")
        self.root.geometry("900x650")
        self.exporter = APACExporter()
        self.db = Database()
        self.exporter.gui_log_callback = self._log_message
        style = ttk.Style()
        style.theme_use('clam')
        self.frame_conexao = ttk.LabelFrame(root_window, text="1. Conexão ao Banco de Dados")
        self.frame_conexao.pack(fill="x", padx=10, pady=5, ipady=5)
        self.frame_filtros = ttk.LabelFrame(root_window, text="2. Filtros e Dados da APAC")
        self.frame_filtros.pack(fill="x", padx=10, pady=5, ipady=5)
        self.frame_acoes = ttk.LabelFrame(root_window, text="3. Ações")
        self.frame_acoes.pack(fill="x", padx=10, pady=5, ipady=5)
        self.frame_log = ttk.LabelFrame(root_window, text="Log de Eventos")
        self.frame_log.pack(fill="both", expand=True, padx=10, pady=5)
        self._criar_widgets_conexao()
        self._criar_widgets_filtros()
        self._criar_widgets_acoes()
        self._criar_widgets_log()
        self._log_message("Interface APAC iniciada. Conecte-se ao banco de dados.")

    def _validate_apac_num(self, P):
        if P.isdigit() and len(P) <= 12:
            return True
        if P == "":
            return True
        return False

    def _criar_widgets_conexao(self):
        conn_fields = [("Banco:", "db_name", "bd0553"), ("Usuário:", "db_user", "postgres"), ("Senha:", "db_password", "postgres", True), ("Host:", "db_host", "localhost"), ("Porta:", "db_port", "5432")]
        for i, (label_text, attr_name, default_val, *is_password) in enumerate(conn_fields):
            row, col_offset = divmod(i, 3)
            ttk.Label(self.frame_conexao, text=label_text).grid(row=row, column=col_offset*2, padx=5, pady=3, sticky="w")
            entry = ttk.Entry(self.frame_conexao, width=18)
            if is_password and is_password[0]: entry.config(show="*")
            entry.insert(0, default_val)
            entry.grid(row=row, column=col_offset*2 + 1, padx=5, pady=3, sticky="ew")
            setattr(self, attr_name, entry)
        self.btn_conectar = ttk.Button(self.frame_conexao, text="Conectar ao BD", command=self.conectar_bd)
        self.btn_conectar.grid(row=0, column=6, padx=10, pady=5, rowspan=2, sticky="ns")

    def _criar_widgets_filtros(self):
        frame_datas = ttk.Frame(self.frame_filtros)
        frame_datas.pack(fill='x', expand=True, padx=5, pady=5)
        ttk.Label(frame_datas, text="Período de Atendimento:").grid(row=0, column=0, sticky="w")
        self.data_inicio_entry = DateEntry(frame_datas, width=12, date_pattern='dd/mm/yyyy')
        self.data_inicio_entry.grid(row=0, column=1, padx=(5,10))
        ttk.Label(frame_datas, text="até").grid(row=0, column=2, padx=(0,10))
        self.data_fim_entry = DateEntry(frame_datas, width=12, date_pattern='dd/mm/yyyy')
        self.data_fim_entry.grid(row=0, column=3, padx=(5,15))
        ttk.Label(frame_datas, text="Competência (AAAAMM):").grid(row=0, column=4, sticky="w")
        self.competencia_entry = ttk.Entry(frame_datas, width=10)
        self.competencia_entry.insert(0, datetime.datetime.now().strftime("%Y%m"))
        self.competencia_entry.grid(row=0, column=5, padx=5)
        ttk.Separator(self.frame_filtros, orient='horizontal').pack(fill='x', expand=True, pady=10)
        frame_dados_apac = ttk.Frame(self.frame_filtros)
        frame_dados_apac.pack(fill='x', expand=True, padx=5, pady=5)
        ttk.Label(frame_dados_apac, text="Data Início Validade (Lote):").grid(row=0, column=0, sticky="w")
        self.apac_data_inicio_validade = DateEntry(frame_dados_apac, width=12, date_pattern='dd/mm/yyyy')
        self.apac_data_inicio_validade.grid(row=0, column=1, padx=(5,15))
        ttk.Label(frame_dados_apac, text="Nº Inicial da APAC (12 dígitos):").grid(row=0, column=2, sticky="w")
        vcmd = (self.root.register(self._validate_apac_num), '%P')
        self.apac_numero_inicial = ttk.Entry(frame_dados_apac, width=15, validate='key', validatecommand=vcmd)
        self.apac_numero_inicial.grid(row=0, column=3, padx=5)
        ttk.Label(frame_dados_apac, text="(Será incrementado)").grid(row=0, column=4, sticky="w", padx=5)

    def _criar_widgets_acoes(self):
        self.btn_exportar_apac = ttk.Button(self.frame_acoes, text="Gerar e Exportar Arquivo APAC", command=self.gerar_e_exportar_apac, state="disabled")
        self.btn_exportar_apac.pack(pady=10, padx=10, fill="x")

    def _criar_widgets_log(self):
        self.log_text_area = tk.Text(self.frame_log, height=10, wrap=tk.WORD, font=('Courier New', 9))
        self.log_text_area.pack(side=tk.LEFT, fill="both", expand=True)
        log_scrollbar = ttk.Scrollbar(self.frame_log, orient="vertical", command=self.log_text_area.yview)
        log_scrollbar.pack(side=tk.RIGHT, fill="y")
        self.log_text_area.config(yscrollcommand=log_scrollbar.set, state="disabled")

    def _log_message(self, message):
        self.log_text_area.config(state="normal")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text_area.see(tk.END)
        self.log_text_area.config(state="disabled")
        self.root.update_idletasks()

    def conectar_bd(self):
        try:
            db_params = { "db_name": self.db_name.get(), "user": self.db_user.get(), "password": self.db_password.get(), "host": self.db_host.get(), "port": self.db_port.get() }
            self._log_message(f"Tentando conectar ao banco: {db_params['db_name']}@{db_params['host']}...")
            sucesso, mensagem = self.db.conectar(**db_params)
            if sucesso:
                self._log_message("Conexão com o banco de dados estabelecida com sucesso!")
                self.exporter.conn = self.db.conn
                messagebox.showinfo("Sucesso", "Conexão ao banco de dados estabelecida!")
                self.btn_exportar_apac.config(state="normal")
            else:
                self._log_message(f"Falha ao conectar ao banco: {mensagem}")
                messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco.\n\nDetalhe: {mensagem}")
        except Exception as e:
            self._log_message(f"Erro inesperado durante a conexão: {str(e)}")
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro ao tentar conectar: {str(e)}")

    def gerar_e_exportar_apac(self):
        """Função a ser chamada pelo botão de exportação."""
        competencia_val = self.competencia_entry.get()
        if not (competencia_val and len(competencia_val) == 6 and competencia_val.isdigit()):
            messagebox.showerror("Entrada Inválida", "Competência deve estar no formato AAAAMM.")
            return
            
        data_inicio_val = self.data_inicio_entry.get_date()
        data_fim_val = self.data_fim_entry.get_date()
        data_inicio_validade_val = self.apac_data_inicio_validade.get_date()
            
        numero_inicial_val = self.apac_numero_inicial.get()
        if not (numero_inicial_val and len(numero_inicial_val) == 12 and numero_inicial_val.isdigit()):
            messagebox.showerror("Entrada Inválida", "O Número Inicial da APAC deve conter exatamente 12 dígitos numéricos.")
            return

        caminho_arquivo = filedialog.asksaveasfilename(
            initialfile=f"AP{self.exporter.config.get('cnes', '')}{competencia_val[4:6]}{competencia_val[3:4]}.TXT",
            defaultextension=".TXT",
            filetypes=[("Arquivos APAC", "*.TXT"), ("Todos os Arquivos", "*.*")],
            title="Salvar Arquivo APAC"
        )
        if not caminho_arquivo:
            self._log_message("Exportação APAC cancelada.")
            return

        params_execucao = {
            'data_inicio': data_inicio_val,
            'data_fim': data_fim_val,
            'competencia': competencia_val,
            'caminho_arquivo': caminho_arquivo,
            'data_inicio_validade': data_inicio_validade_val,
            'numero_inicial': numero_inicial_val
        }

        self._log_message(f"Iniciando geração de arquivo APAC para {caminho_arquivo}...")
        self.root.update_idletasks()

        sucesso, resultado = self.exporter.processar_e_gerar_apac(params_execucao)

        if sucesso:
            msg = f"Arquivo APAC gerado com sucesso: {resultado}"
            self._log_message(msg)
            messagebox.showinfo("Sucesso", msg)
        else:
            msg = f"Falha ao gerar arquivo APAC: {resultado}"
            self._log_message(msg)
            messagebox.showerror("Erro", msg)

def main():
    """Função principal para iniciar a GUI da APAC."""
    app_root = tk.Tk()
    gui_app = APACExporterGUI(app_root)
    app_root.mainloop()

if __name__ == "__main__":
    main()
