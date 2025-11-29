# Arquivo: ciha_exporter.py

import os
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from sqlalchemy import text
import pandas as pd
import traceback
from shared.mapeamento_profissionais import carregar_mapeamento_profissionais
from shared.database import Database
from shared.mapeamento_procedimentos import carregar_tabela_procedimentos_cid
from tkcalendar import DateEntry

class CIHAExporter:
    def __init__(self):
        self.conn = None
        self.gui_log_callback = None
        self.config = {}
        self.registros_brutos_para_analise = []

    def _log_message_gui(self, message):
        if self.gui_log_callback and callable(self.gui_log_callback):
            self.gui_log_callback(message)
            
    def carregar_mapeamento_procedimentos(self, cod_procs_bd_unicos):
        mapeamento_proc = {}
        if not self.conn or not cod_procs_bd_unicos:
            return mapeamento_proc
        try:
            from sqlalchemy import table, column, select
            procedimentos_table = table("procedimentos", column("id_procedimento"), column("codigo_procedimento"), schema="sigh")
            cod_procs_list = [str(c) for c in cod_procs_bd_unicos if c]
            if not cod_procs_list:
                return mapeamento_proc
            
            query = select(
                procedimentos_table.c.id_procedimento, 
                procedimentos_table.c.codigo_procedimento
            ).where(procedimentos_table.c.id_procedimento.in_(cod_procs_list))
            
            result = self.conn.execute(query)
            for row in result: 
                mapeamento_proc[str(row.id_procedimento)] = str(row.codigo_procedimento)
        except Exception as e:
            self._log_message_gui(f"Erro ao carregar mapeamento de procedimentos SIGH: {str(e)}")
        return mapeamento_proc

    def _build_sql_ciha(self, data_inicio, data_fim, unidade_selecionada):
        data_inicio_str = data_inicio.isoformat()
        data_fim_str = data_fim.isoformat()

        mapeamento = carregar_mapeamento_profissionais()
        lista_de_codigos = list(mapeamento.keys())
        codigos_profissionais = ", ".join(f"'{str(codigo)}'" for codigo in lista_de_codigos)

        if not codigos_profissionais:
            raise ValueError("A lista de códigos de profissionais do mapeamento está vazia.")

        filtro_profissionais_sql = f"AND fi.cod_medico IN ({codigos_profissionais})"
        
        sql_query = f"""
        WITH RankedEnderecos AS (
            SELECT
                ep.cod_paciente, ep.cod_logradouro, ep.numero, ep.complemento,
                ROW_NUMBER() OVER(PARTITION BY ep.cod_paciente ORDER BY ep.data_hora_atualizacao DESC, ep.data_hora_criacao DESC) as rn
            FROM sigh.enderecos ep
            WHERE ep.ativo = 't'
        )
        SELECT DISTINCT l.id_lancamento,
            v_pac.cartao_sus AS nu_cns,
            p.nm_paciente AS no_paciente,
            p.data_nasc AS dt_nascimento,
            p.cod_sexo AS tp_sexo,
            fi.data_atendimento AS dt_admissao,
            fi.data_atendimento AS dt_saida,
            l.cod_cid,
            fi.diagnostico,
            l.cod_proc,
            l.quantidade,
            logradouros_pac.logradouro AS ds_logradouro,
            enderecos_pac.numero AS nu_logradouro,
            enderecos_pac.complemento AS ds_complemento,
            logradouros_pac.cep AS co_cep,
            logradouros_pac.municipio AS co_municipio,
            logradouros_pac.uf AS sg_uf,
            p.spp AS nu_prontuario,
            v_pac.nm_unidade,
            fi.tipo_atend
        FROM sigh.lancamentos l
        JOIN sigh.contas c ON l.cod_conta = c.id_conta
        JOIN sigh.ficha_amb_int fi ON c.cod_fia = fi.id_fia
        JOIN sigh.pacientes p ON fi.cod_paciente = p.id_paciente
        LEFT JOIN sigh.v_cons_pacientes_laboratorios v_pac ON p.id_paciente = v_pac.registro
        LEFT JOIN RankedEnderecos AS enderecos_pac ON p.id_paciente = enderecos_pac.cod_paciente AND enderecos_pac.rn = 1
        LEFT JOIN endereco_sigh.logradouros AS logradouros_pac ON enderecos_pac.cod_logradouro = logradouros_pac.id_logradouro
        WHERE fi.data_atendimento BETWEEN :inicio AND :fim {filtro_profissionais_sql}
        ORDER BY p.nm_paciente, l.id_lancamento
        """
        
        sql_params = {'inicio': data_inicio_str, 'fim': data_fim_str}
        
        return sql_query, sql_params

    def aplicar_filtro_procedimentos(self, registros, filtro_texto):
        if not filtro_texto.strip():
            self._log_message_gui("Nenhum filtro de procedimento aplicado. Exportando todos os registros da consulta.")
            return registros

        self._log_message_gui("Aplicando filtro de contagem de procedimentos...")
        try:
            regras_filtro = {}
            for linha in filtro_texto.strip().split('\n'):
                if '=' in linha:
                    partes = linha.split('=')
                    codigo = partes[0].strip().split('-')[0].strip()
                    quantidade = int(partes[1].strip().split(' ')[0].strip())
                    if len(codigo) == 10 and codigo.isdigit():
                        regras_filtro[codigo] = quantidade
            
            if not regras_filtro:
                self._log_message_gui("Formato do filtro inválido. Nenhum procedimento válido encontrado.")
                return registros

            df = pd.DataFrame(registros)
            
            # Garante que a coluna de procedimento exista para o filtro
            if 'co_procedimento_sigtap' not in df.columns:
                self._log_message_gui("Erro: Coluna 'co_procedimento_sigtap' não encontrada para aplicar o filtro.")
                return registros

            # Cria um DataFrame vazio para acumular os resultados
            df_filtrado_final = pd.DataFrame(columns=df.columns)
            
            # Agrupa por procedimento e aplica o limite de quantidade para cada um
            for codigo, quantidade in regras_filtro.items():
                grupo_procedimento = df[df['co_procedimento_sigtap'] == codigo]
                df_filtrado_final = pd.concat([df_filtrado_final, grupo_procedimento.head(quantidade)])

            self._log_message_gui(f"Filtro aplicado. Total de registros após a filtragem: {len(df_filtrado_final)}")
            return df_filtrado_final.to_dict('records')

        except Exception as e:
            self._log_message_gui(f"Erro ao aplicar filtro de procedimentos: {e}")
            traceback.print_exc()
            return registros

    def processar_e_gerar_ciha(self, params):
        if not self.conn: return False, "Sem conexão com o banco."
        try:
            self._log_message_gui("Iniciando consulta de dados para CIHA...")
            sql, sql_params = self._build_sql_ciha(params['data_inicio'], params['data_fim'], params['unidade'])
            
            result = self.conn.execute(text(sql), sql_params)
            self.registros_brutos_para_analise = [dict(row._mapping) for row in result.fetchall()]
            self._log_message_gui(f"{len(self.registros_brutos_para_analise)} registros brutos encontrados.")

            if not self.registros_brutos_para_analise:
                return False, "Nenhum registro encontrado para os filtros selecionados."

            self._log_message_gui("Mapeando códigos de procedimento e traduzindo CID...")
            tabela_proc_cid = carregar_tabela_procedimentos_cid()
            cod_procs_unicos = {reg.get('cod_proc') for reg in self.registros_brutos_para_analise if reg.get('cod_proc')}
            mapeamento_curto = self.carregar_mapeamento_procedimentos(cod_procs_unicos)

            registros_processados = []
            for reg in self.registros_brutos_para_analise:
                cod_proc_interno = reg.get('cod_proc')
                codigo_curto = mapeamento_curto.get(str(cod_proc_interno))
                proc_info = tabela_proc_cid.get(codigo_curto) if codigo_curto else None
                reg['co_procedimento_sigtap'] = proc_info.get('codigo_sigtap') if proc_info else None
                cid_final = ''
                cid_do_lancamento = str(reg.get('cod_cid') or '').strip().replace('.', '')
                cid_sugerido = proc_info.get('cid_sugestao', '') if proc_info else None
                is_cid10_format = len(cid_do_lancamento) >= 3 and cid_do_lancamento[0].isalpha()
                if is_cid10_format:
                    cid_final = cid_do_lancamento
                elif cid_sugerido:
                    cid_final = cid_sugerido
                if not cid_final:
                    cid_final = 'R688'
                reg['cid_final_tratado'] = cid_final.upper()
                registros_processados.append(reg)
            
            # Aplica o novo filtro de quantidade
            registros_filtrados = self.aplicar_filtro_procedimentos(registros_processados, params.get('filtro_procedimentos', ''))
                
            self._log_message_gui("Processamento finalizado.")
            return True, registros_filtrados

        except Exception as e:
            error_msg = f"Erro fatal ao processar e gerar CIHA: {e}"
            self._log_message_gui(error_msg)
            traceback.print_exc()
            return False, str(e)

    def gerar_arquivo_ciha_formatado(self, registros, params):
        def formatar_numero(valor, tamanho):
            if valor is None: valor = 0
            try: valor_inteiro = int(float(valor))
            except (ValueError, TypeError): valor_inteiro = 0
            return str(valor_inteiro).zfill(tamanho)

        def formatar_texto(valor, tamanho, default=''):
            return str(valor or default).strip().ljust(tamanho)
        
        caminho_arquivo = params.get('caminho_arquivo')
        if not caminho_arquivo:
            return False, "Caminho do arquivo não foi fornecido para a geração."

        try:
            with open(caminho_arquivo, 'w', encoding='latin-1', newline='\n') as f:
                sequencial_linha = 1
                for reg in registros:
                    linha = [
                        formatar_numero(params['competencia'], 6),
                        formatar_numero(params['cnes'], 7),
                        formatar_texto('I', 1),
                        formatar_numero(reg.get('co_procedimento_sigtap') or reg.get('cod_proc'), 10),
                        formatar_numero(reg.get('quantidade'), 6),
                        formatar_numero('11', 2),
                        formatar_numero('', 8),
                        formatar_numero(reg.get('dt_admissao').strftime('%d%m%Y') if reg.get('dt_admissao') else '', 8),
                        formatar_numero(reg.get('dt_saida').strftime('%d%m%Y') if reg.get('dt_saida') else '', 8),
                        formatar_numero('01', 2),
                        formatar_numero('12', 2),
                        formatar_numero('', 2),
                        formatar_texto(reg.get('cid_final_tratado'), 4),
                        formatar_texto('', 4),
                        formatar_numero('', 11),
                        formatar_numero('', 11),
                        formatar_texto('', 30),
                        formatar_numero('', 13),
                        formatar_texto('', 15),
                        formatar_texto(reg.get('nu_prontuario'), 17),
                        formatar_numero(reg.get('nu_cns'), 15),
                        formatar_texto(reg.get('no_paciente'), 70),
                        formatar_numero(reg.get('dt_nascimento').strftime('%d%m%Y') if reg.get('dt_nascimento') else '', 8),
                        formatar_texto('M' if str(reg.get('tp_sexo')) == '1' else 'F', 1),
                        formatar_texto(reg.get('ds_logradouro'), 25),
                        formatar_texto(reg.get('nu_logradouro'), 5, default='S/N'),
                        formatar_texto(reg.get('ds_complemento'), 15),
                        formatar_numero(reg.get('co_cep'), 8),
                        formatar_numero(reg.get('co_municipio'), 7),
                        formatar_texto(reg.get('sg_uf'), 2),
                        formatar_numero(str(sequencial_linha % 10), 1),
                    ]
                    
                    linha_str = "".join(linha)
                    
                    tamanho_atual = len(linha_str)
                    tamanho_filler = 450 - tamanho_atual
                    if tamanho_filler > 0:
                        linha_str += formatar_texto('', tamanho_filler)

                    f.write(linha_str[:450] + '\n')
                    sequencial_linha += 1
            
            return True, caminho_arquivo
        except Exception as e:
            self._log_message_gui(f"Erro ao escrever o arquivo final: {e}")
            traceback.print_exc()
            return False, str(e)
            
    def gerar_analise_divergencia(self, caminho_arquivo):
        if not self.registros_brutos_para_analise:
            return False, "Não há dados brutos para analisar. Execute uma consulta primeiro."
        try:
            self._log_message_gui("Gerando arquivo de análise de divergência...")
            df = pd.DataFrame(self.registros_brutos_para_analise)
            df.to_excel(caminho_arquivo, sheet_name="Analise_Divergencia_CIHA", index=False)
            return True, caminho_arquivo
        except Exception as e:
            self._log_message_gui(f"Erro ao gerar análise de divergência: {e}")
            return False, str(e)

class CIHAExporterGUI:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Exportador CIHA (SIGH)")
        self.root.geometry("700x750") # Aumenta a altura da janela
        self.exporter = CIHAExporter()
        self.db = Database()
        self.exporter.gui_log_callback = self._log_message
        style = ttk.Style()
        style.theme_use('clam')
        self.frame_conexao = ttk.LabelFrame(root_window, text="1. Conexão")
        self.frame_conexao.pack(fill="x", padx=10, pady=5)
        self.frame_filtros = ttk.LabelFrame(root_window, text="2. Parâmetros de Exportação")
        self.frame_filtros.pack(fill="x", padx=10, pady=5, ipady=5)
        self.frame_acoes = ttk.LabelFrame(root_window, text="3. Ações")
        self.frame_acoes.pack(fill="x", padx=10, pady=5)
        self.frame_log = ttk.LabelFrame(root_window, text="Log de Eventos")
        self.frame_log.pack(fill="both", expand=True, padx=10, pady=5)
        self._criar_widgets_conexao()
        self._criar_widgets_filtros()
        self._criar_widgets_acoes()
        self._criar_widgets_log()
        self._log_message("Interface CIHA iniciada. Conecte-se ao banco de dados.")

    def _criar_widgets_conexao(self):
        ttk.Label(self.frame_conexao, text="Status:").pack(side="left", padx=5)
        self.lbl_status_conexao = ttk.Label(self.frame_conexao, text="Desconectado", foreground="red")
        self.lbl_status_conexao.pack(side="left", padx=5)
        self.btn_conectar = ttk.Button(self.frame_conexao, text="Conectar ao BD", command=self.conectar_bd)
        self.btn_conectar.pack(side="right", padx=10, pady=5)

    def _criar_widgets_filtros(self):
        ttk.Label(self.frame_filtros, text="Competência (no arquivo):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.competencia_entry = ttk.Entry(self.frame_filtros, width=10)
        self.competencia_entry.insert(0, datetime.datetime.now().strftime("%Y%m"))
        self.competencia_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.frame_filtros, text="CNES do Estabelecimento:").grid(row=0, column=2, padx=(15, 5), pady=5, sticky="w")
        self.cnes_entry = ttk.Entry(self.frame_filtros, width=10)
        self.cnes_entry.insert(0, "2560372")
        self.cnes_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(self.frame_filtros, text="Período do Atendimento:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.data_inicio_entry = DateEntry(self.frame_filtros, width=12, date_pattern='dd/mm/yyyy')
        self.data_inicio_entry.grid(row=1, column=1, padx=5, pady=5)
        self.data_fim_entry = DateEntry(self.frame_filtros, width=12, date_pattern='dd/mm/yyyy')
        self.data_fim_entry.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(self.frame_filtros, text="Unidade Organizacional:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.unidade_combo = ttk.Combobox(self.frame_filtros, width=50, state="readonly")
        self.unidade_combo.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # --- NOVO WIDGET PARA O FILTRO DE PROCEDIMENTOS ---
        ttk.Label(self.frame_filtros, text="Filtro de Quantidade por Procedimento (opcional):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.filtro_proc_text = tk.Text(self.frame_filtros, height=5, width=60)
        self.filtro_proc_text.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        # --- FIM DO NOVO WIDGET ---

        self.debug_mode_var = tk.BooleanVar()
        self.debug_check = ttk.Checkbutton(self.frame_filtros, text="Ativar Log de Depuração", variable=self.debug_mode_var)
        self.debug_check.grid(row=4, column=1, columnspan=2, padx=5, pady=10, sticky="w")

    def _criar_widgets_acoes(self):
        self.btn_exportar_ciha = ttk.Button(self.frame_acoes, text="Gerar e Exportar Arquivo CIHA", command=self.gerar_e_exportar_ciha)
        self.btn_exportar_ciha.pack(side="left", pady=10, padx=10, fill="x", expand=True)

        self.btn_analise_divergencia = ttk.Button(self.frame_acoes, text="Gerar Análise de Divergência", command=self.gerar_analise_divergencia_handler, state="disabled")
        self.btn_analise_divergencia.pack(side="left", pady=10, padx=10, fill="x", expand=True)

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
    
    def carregar_unidades(self):
        if not self.db.conn:
            self._log_message("Não é possível carregar unidades. Sem conexão com o BD.")
            return
        try:
            self._log_message("Carregando lista de unidades do banco de dados...")
            query = text("SELECT DISTINCT nm_unidade FROM sigh.unidades WHERE ativo = 't' ORDER BY nm_unidade")
            result = self.db.conn.execute(query)
            unidades = [row[0] for row in result if row[0] is not None]
            self.unidade_combo['values'] = ["TODAS AS UNIDADES"] + unidades
            self.unidade_combo.current(0)
            self._log_message("Lista de unidades carregada com sucesso.")
        except Exception as e:
            self._log_message(f"Erro ao carregar unidades: {e}")
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível carregar a lista de unidades:\n{e}")

    def conectar_bd(self):
        db_params = {"db_name": "bd0553", "user": "postgres", "password": "postgres", "host": "localhost", "port": "5432"}
        self._log_message(f"Tentando conectar ao banco: {db_params['db_name']}@{db_params['host']}...")
        sucesso, mensagem = self.db.conectar(**db_params)
        if sucesso:
            self._log_message("Conexão com o banco de dados estabelecida com sucesso!")
            self.exporter.conn = self.db.conn
            self.lbl_status_conexao.config(text="Conectado", foreground="green")
            self.btn_exportar_ciha.config(state="normal")
            self.btn_conectar.config(state="disabled")
            self.carregar_unidades()
        else:
            self._log_message(f"Falha ao conectar ao banco: {mensagem}")
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar.\n\nDetalhe: {mensagem}")

    def gerar_e_exportar_ciha(self):
        self.btn_exportar_ciha.config(state="disabled")
        self.btn_analise_divergencia.config(state="disabled")
        self.root.update_idletasks()

        try:
            competencia_val = self.competencia_entry.get()
            cnes_val = self.cnes_entry.get()
            unidade_val = self.unidade_combo.get()
            debug_val = self.debug_mode_var.get()
            data_inicio_val = self.data_inicio_entry.get_date()
            data_fim_val = self.data_fim_entry.get_date()
            filtro_proc_val = self.filtro_proc_text.get("1.0", tk.END)

            if not (competencia_val and len(competencia_val) == 6 and competencia_val.isdigit()):
                messagebox.showerror("Entrada Inválida", "Competência deve estar no formato AAAAMM.")
                return
            if not (cnes_val and len(cnes_val) == 7 and cnes_val.isdigit()):
                messagebox.showerror("Entrada Inválida", "CNES deve conter 7 dígitos numéricos.")
                return
            
            params = {
                'competencia': competencia_val, 'cnes': cnes_val, 'unidade': unidade_val,
                'debug_mode': debug_val, 'data_inicio': data_inicio_val, 'data_fim': data_fim_val,
                'filtro_procedimentos': filtro_proc_val
            }

            self._log_message(f"Iniciando processo de consulta e geração...")
            
            sucesso, resultado = self.exporter.processar_e_gerar_ciha(params)

            if sucesso:
                caminho_arquivo = filedialog.asksaveasfilename(
                    initialfile=f"CIHA01{cnes_val}{competencia_val}.TXT",
                    defaultextension=".TXT", filetypes=[("Arquivos CIHA", "*.TXT")], title="Salvar Arquivo CIHA"
                )
                if not caminho_arquivo:
                    self._log_message("Exportação CIHA cancelada pelo usuário.")
                    return
                
                params['caminho_arquivo'] = caminho_arquivo
                
                sucesso_final, resultado_final = self.exporter.gerar_arquivo_ciha_formatado(resultado, params)
                
                if sucesso_final:
                    msg = f"Arquivo CIHA gerado com sucesso: {resultado_final}"
                    self._log_message(msg)
                    messagebox.showinfo("Sucesso", msg)
                else:
                    msg = f"Falha ao gerar arquivo CIHA: {resultado_final}"
                    self._log_message(msg)
                    messagebox.showerror("Erro", msg)

            else:
                msg = f"Falha no processamento de dados: {resultado}"
                self._log_message(msg)
                messagebox.showerror("Erro", msg)

        finally:
            self.btn_exportar_ciha.config(state="normal")
            if self.exporter.registros_brutos_para_analise:
                self.btn_analise_divergencia.config(state="normal")

    def gerar_analise_divergencia_handler(self):
        if not self.exporter.registros_brutos_para_analise:
            messagebox.showwarning("Sem Dados", "Execute a consulta 'Gerar e Exportar Arquivo CIHA' primeiro.")
            return

        caminho_arquivo = filedialog.asksaveasfilename(
            initialfile=f"Analise_Divergencia_CIHA_{self.competencia_entry.get()}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Arquivos Excel", "*.xlsx")],
            title="Salvar Análise de Divergência"
        )
        if not caminho_arquivo:
            self._log_message("Geração de análise de divergência cancelada.")
            return

        sucesso, resultado = self.exporter.gerar_analise_divergencia(caminho_arquivo)

        if sucesso:
            msg = f"Arquivo de análise gerado com sucesso: {resultado}"
            self._log_message(msg)
            messagebox.showinfo("Sucesso", msg)
        else:
            msg = f"Falha ao gerar arquivo de análise: {resultado}"
            self._log_message(msg)
            messagebox.showerror("Erro", msg)

def main():
    app_root = tk.Tk()
    gui_app = CIHAExporterGUI(app_root)
    app_root.mainloop()

if __name__ == "__main__":
    main()