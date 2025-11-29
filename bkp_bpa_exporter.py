import os
import pandas as pd
from sqlalchemy import text
import datetime
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
import csv


# Importações dos módulos compartilhados
from shared.database import Database
from shared.mapeamento_procedimentos import carregar_tabela_procedimentos_cid
from shared.mapeamento_tp_logradouro_sigh_bpa import carregar_mapeamento_logradouros
from shared.mapeamento_profissionais import carregar_mapeamento_profissionais

class BPAExporter:
    """
    Classe "motor" responsável pela lógica de negócio da exportação de arquivos BPA.
    """
    def __init__(self):
        self.conn = None
        self.mapeamentos_faltantes_log = set()
        self.gui_log_callback = None
        self.registros_do_banco_para_indicadores = []

        self.config = {
            'orgao_responsavel': 'APAE DE COLINAS DO TOCANTINS',
            'sigla_orgao': 'APAE',
            'cgc_cpf': '25062282000182',
            'orgao_destino': 'SESAU TO',
            'indicador_destino': 'E',
            'versao_sistema': 'V04.10',
            'cnes': '2560372',
            'default_ine': '          '
        }
        
        self.cbo_override_map = {
            '43': '225133', '4':  '225275', '68': '225265', '67': '225125', '76': '225133',
            '81': '225265', '33': '225275', '70': '225270', '35': '225133', '86': '225160',
            '89': '225125'
        }

    def _log_message_gui(self, message):
        if self.gui_log_callback and callable(self.gui_log_callback):
            self.gui_log_callback(message)

    def _build_sql_completo(self, coluna_data_filtro, alias_tabela_filtro="l"):
        return f"""
        WITH RankedEnderecos AS (
            SELECT
                ep.cod_paciente, ep.cod_logradouro, ep.numero,
                ROW_NUMBER() OVER(PARTITION BY ep.cod_paciente ORDER BY ep.data_hora_atualizacao DESC, ep.data_hora_criacao DESC, ep.id_endereco DESC) as rn
            FROM sigh.enderecos ep
            WHERE ep.ativo = 't' AND ep.cod_logradouro IS NOT NULL
        ),
        CidPrincipalFia AS (
            SELECT
                cf.cod_fia,
                c.codigo,
                ROW_NUMBER() OVER(PARTITION BY cf.cod_fia ORDER BY cf.ordem ASC, cf.id_cid_fia ASC) as rn_cid
            FROM
                sigh.cids_fia cf
            JOIN
                sigh.cids c ON cf.cod_cid_fia = c.id_cid
            WHERE
                cf.ativo = 't' AND c.ativo = 't'
        )
        SELECT
            l.id_lancamento, l.cod_proc, l.quantidade, l.cod_cid AS lanc_cid,
            fi.diagnostico AS diagnostico_ficha,
            fi.matricula AS cnspac_paciente_original,
            cid_principal.codigo AS cid_da_fia,
            l.cod_serv, l.data AS data_atendimento_lancamento,
            {alias_tabela_filtro}.{coluna_data_filtro} AS data_filtro_usada,
            c.competencia AS conta_competencia,
            p.id_paciente, p.nm_paciente, p.data_nasc, p.cod_sexo AS sexo_paciente,
            p.cod_raca_etnia, p.cod_etnia_indigena AS cod_etnia_paciente_original,
            p.cod_nacionalidade AS nacionalidade_paciente,
            pr_lanc.id_prestador AS id_prestador_lancamento,
            pr_lanc.nm_prestador AS nm_prestador_ficha,
            pr_lanc.cns AS cns_profissional_lancamento,
            vcpc.codigo_cbo AS cbo_profissional_view,
            vcre.codigo_raca_etnia AS codigo_raca_etnia_view,
            logradouros_pac.cep AS vcp_cep,
            logradouros_pac.tp_logradouro AS vcp_tp_logradouro,
            logradouros_pac.logradouro AS vcp_logradouro,
            enderecos_pac.numero AS vcp_numero,
            logradouros_pac.bairro_inicial AS vcp_bairro_inicial,
            aihu_cep_ibge.ibge AS ibge_por_cep
        FROM
            sigh.lancamentos AS l
        JOIN sigh.contas AS c ON l.cod_conta = c.id_conta
        JOIN sigh.ficha_amb_int AS fi ON c.cod_fia = fi.id_fia
        LEFT JOIN sigh.pacientes AS p ON fi.cod_paciente = p.id_paciente
        LEFT JOIN CidPrincipalFia AS cid_principal ON fi.id_fia = cid_principal.cod_fia AND cid_principal.rn_cid = 1
        LEFT JOIN sigh.prestadores AS pr_lanc ON l.cod_prestador = pr_lanc.id_prestador
        LEFT JOIN sigh.v_cons_prestadores_cbos_scola AS vcpc ON l.cod_prestador = vcpc.id_prestador
        LEFT JOIN sigh.v_cons_racas_etnias_scola AS vcre ON p.cod_raca_etnia = vcre.id_raca_etnia
        LEFT JOIN RankedEnderecos AS enderecos_pac ON p.id_paciente = enderecos_pac.cod_paciente AND enderecos_pac.rn = 1
        LEFT JOIN endereco_sigh.logradouros AS logradouros_pac ON enderecos_pac.cod_logradouro = logradouros_pac.id_logradouro
        LEFT JOIN aihu.ceps_municipios_ibges AS aihu_cep_ibge ON logradouros_pac.cep = aihu_cep_ibge.cep
        """

    def carregar_mapeamento_procedimentos(self, cod_procs_bd_unicos):
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
            self._log_message_gui(f"Erro ao carregar mapeamento de procedimentos: {str(e)}")
        return mapeamento_proc

    def consultar_dados_completo(self, data_inicio, data_fim, competencia=None, criterio_data="lancamento"):
        if not self.conn: return [], {}, 0
        self.mapeamentos_faltantes_log.clear()
        try:
            competencia_gui = competencia or datetime.datetime.now().strftime("%Y%m")
            competencia_bd_formatada = competencia_gui[4:] + "/" + competencia_gui[:4]  # Formato MM/YYYY
            data_inicio_str = data_inicio.isoformat()
            data_fim_str = data_fim.isoformat()

            coluna_data_para_select_no_alias = "data"
            alias_tabela_para_select = "l"
            if criterio_data == "competencia":
                coluna_data_para_select_no_alias = "competencia"
                alias_tabela_para_select = "c"

            sql_base = self._build_sql_completo(coluna_data_para_select_no_alias, alias_tabela_para_select)
            
            condicoes_where_comuns_sigh = ["c.ativo = 't'", "c.status_conta = 'A'", "l.cod_proc IS NOT NULL"]
            if criterio_data == "competencia":
                condicoes_especificas = [f"c.competencia = '{competencia_bd_formatada}'"] + condicoes_where_comuns_sigh
                where_clause_final = "WHERE " + " AND ".join(condicoes_especificas)
            else:
                condicao_data = f"l.data BETWEEN '{data_inicio_str}' AND '{data_fim_str}'"
                condicoes_com_data = [condicao_data] + condicoes_where_comuns_sigh
                where_clause_final = "WHERE " + " AND ".join(condicoes_com_data)

            order_by_clause = "ORDER BY pr_lanc.cns, l.data, l.id_lancamento"
            full_sql_query_str = sql_base + "\n" + where_clause_final + "\n" + order_by_clause
            
            self._log_message_gui("Executando consulta principal no banco de dados...")
            result = self.conn.execute(text(full_sql_query_str))
            registros_do_banco = [dict(row._mapping) for row in result.fetchall()]
            self.registros_do_banco_para_indicadores = registros_do_banco
            self._log_message_gui(f"Consulta SQL retornou {len(registros_do_banco)} linhas brutas.")

            if not registros_do_banco: return [], {}, 0

            cod_procs_unicos = {reg.get('cod_proc') for reg in registros_do_banco if reg.get('cod_proc')}
            mapeamento_proc = self.carregar_mapeamento_procedimentos(cod_procs_unicos)
            tabela_proc_cid = carregar_tabela_procedimentos_cid()

            registros_bpa, registros_apac, contadores_modalidade = [], [], {}
            for reg in registros_do_banco:
                codigo_curto = mapeamento_proc.get(str(reg.get('cod_proc')))
                proc_info = tabela_proc_cid.get(codigo_curto) if codigo_curto else None
                if proc_info:
                    categoria = proc_info.get('categoria', 'BPA')
                    if categoria.upper() == 'APAC':
                        registros_apac.append(reg)
                    else:
                        registros_bpa.append(reg)
                        modalidade = proc_info.get('modalidade', 'Não Mapeado')
                        contadores_modalidade[modalidade] = contadores_modalidade.get(modalidade, 0) + 1
                else:
                    registros_bpa.append(reg)
                    contadores_modalidade['Não Mapeado'] = contadores_modalidade.get('Não Mapeado', 0) + 1
                    if reg.get('cod_proc'):
                        self.mapeamentos_faltantes_log.add((codigo_curto or f"ID_BD:{reg.get('cod_proc')}", str(reg.get('cod_proc'))))
            
            self._log_message_gui(f"Classificação: {len(registros_bpa)} procedimentos para BPA, {len(registros_apac)} para APAC (ignorados).")

            if registros_bpa:
                registros_processados = self.processar_registros_bpa_i_completo(registros_bpa, competencia_gui)
                if self.mapeamentos_faltantes_log: self._escrever_log_mapeamentos_faltantes()
                return registros_processados, contadores_modalidade, len(registros_apac)
            else:
                return [], contadores_modalidade, len(registros_apac)
        except Exception as e:
            self._log_message_gui(f"Erro na consulta: {e}")
            import traceback; traceback.print_exc()
            return [], {}, 0
    
    def calcular_idade(self, data_nascimento):
        """
        Calcula a idade de uma pessoa a partir da data de nascimento.
        """
        hoje = datetime.date.today()
        if not isinstance(data_nascimento, (datetime.datetime, datetime.date)):
            try:
                nascimento = datetime.datetime.strptime(str(data_nascimento), '%Y%m%d').date()
            except (ValueError, TypeError):
                return 0 
        else:
            if isinstance(data_nascimento, datetime.datetime):
                nascimento = data_nascimento.date()
            else:
                nascimento = data_nascimento

        if not nascimento:
            return 0
            
        idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
        return idade

    def processar_registros_bpa_i_completo(self, registros_bd, competencia):
        registros_bpa_i_sem_numeracao = []
        tabela_proc_cid = carregar_tabela_procedimentos_cid()
        cod_procs_bd_unicos = list(set([reg.get('cod_proc') for reg in registros_bd if reg.get('cod_proc')]))
        mapeamento_proc = self.carregar_mapeamento_procedimentos(cod_procs_bd_unicos)
        
        mapeamento_logradouros = carregar_mapeamento_logradouros()
        mapeamento_profissionais = carregar_mapeamento_profissionais()

        for reg_data in registros_bd:
            id_prestador = str(reg_data.get('id_prestador_lancamento'))
            cns_med_val = str(reg_data.get('cns_profissional_lancamento') or '').strip()
            cns_med = cns_med_val.ljust(15) if cns_med_val else ' ' * 15
            
            cbo_override = self.cbo_override_map.get(id_prestador)
            if cbo_override:
                cbo_val = cbo_override
                self._log_message_gui(f"REGRA: CBO para o prestador ID {id_prestador} alterado para '{cbo_val}'.")
            else:
                cbo_val = str(reg_data.get('cbo_profissional_view') or '').strip()
            cbo = cbo_val.ljust(6)[:6] if cbo_val else ' ' * 6
            
            data_atend_obj = reg_data.get('data_atendimento_lancamento')
            data_atend_str = data_atend_obj.strftime('%Y%m%d') if data_atend_obj else competencia + "01"
            nome_paciente_val = str(reg_data.get('nm_paciente') or '').strip()
            nome_paciente = nome_paciente_val.ljust(30)[:30]
            data_nasc_obj = reg_data.get('data_nasc')
            data_nasc_str = data_nasc_obj.strftime('%Y%m%d') if data_nasc_obj else ''
            cnspac_val = str(reg_data.get('cnspac_paciente_original') or '').strip()
            cnspac = cnspac_val.ljust(15) if cnspac_val else ' ' * 15
            sexo_bd = str(reg_data.get('sexo_paciente') or '').strip()
            sexo = 'M' if sexo_bd == '1' else 'F'
            ibge_val = str(reg_data.get('ibge_por_cep') or '').strip()
            cod_ibge_paciente = ibge_val.ljust(6)[:6] if ibge_val else ' ' * 6
            idade = 0
            if data_nasc_obj and data_atend_obj:
                idade = self.calcular_idade(data_nasc_obj)
            idade_str = str(min(max(idade, 0), 130)).zfill(3)
            raca_val = str(reg_data.get('codigo_raca_etnia_view') or '99').strip()
            raca = raca_val.zfill(2)
            etnia_val = str(reg_data.get('cod_etnia_indigena') or '').strip() if raca == '05' else ''
            etnia = etnia_val.zfill(4) if etnia_val else '    '
            cod_proc_bd = reg_data.get('cod_proc')
            codigo_curto = mapeamento_proc.get(str(cod_proc_bd))
            
            proc_info = tabela_proc_cid.get(codigo_curto, {}) if codigo_curto else {}
            
            cod_proc_sigtap_original = proc_info.get('codigo_sigtap', '0301010048')

            cod_proc_sigtap_final = cod_proc_sigtap_original
            proc_info_final = proc_info

            if id_prestador == '35' and cod_proc_sigtap_original == '0301070075':
                cod_proc_sigtap_final = '0301010072'
                proc_info_final = tabela_proc_cid.get('72', {})
                self._log_message_gui(f"REGRA: Procedimento '0301070075' do prestador ID 35 alterado para '{cod_proc_sigtap_final}'.")

            servico_val = proc_info_final.get('servico', '')
            classificacao_val = proc_info_final.get('classificacao', '')

            if not servico_val and not classificacao_val:
                info_profissional = mapeamento_profissionais.get(id_prestador, {})
                servico_val = info_profissional.get('servico', '')
                classificacao_val = info_profissional.get('classificacao', '')
                if servico_val:
                    self._log_message_gui(f"REGRA: Usando Serv/Class ({servico_val}/{classificacao_val}) do profissional ID {id_prestador} pois o procedimento não possui.")
            
            quantidade_final = '000001'
            if cod_proc_sigtap_final == '0701050020':
                quantidade_final = '000030'
            
            cid_obrigatorio = proc_info_final.get('cid_obrigatorio', False)
            cid_sugestao = proc_info_final.get('cid_sugestao')
            
            cid_banco_primario = reg_data.get('cid_da_fia') or reg_data.get('lanc_cid')
            cid_banco_secundario = reg_data.get('diagnostico_ficha')
            
            cid_val = str(cid_banco_primario or cid_banco_secundario or cid_sugestao or ('Z000' if cid_obrigatorio else ''))
            
            cid_formatado = cid_val.strip().upper().replace('.', '')
            cid = cid_formatado.ljust(4)[:4] if cid_formatado else '    '

            numero_val = str(reg_data.get('vcp_numero') or '').strip()
            numero = '00000' if not numero_val else numero_val.ljust(5)[:5]
            
            nome_profissional_val = str(reg_data.get('nm_prestador_ficha') or '').strip()
            
            tipo_logradouro_texto = str(reg_data.get('vcp_tp_logradouro') or '').strip().upper()
            codigo_logradouro = mapeamento_logradouros.get(tipo_logradouro_texto, '000')
            
            registro_bpa_i = {
                'prd_ident': '03', 'prd_cnes': self.config.get('cnes').ljust(7),
                'prd_cmp': competencia, 'prd_cnsmed': cns_med, 'prd_cbo': cbo,
                'prd_dtaten': data_atend_str, 'prd_flh': '   ', 'prd_seq': '  ',
                'prd_pa': cod_proc_sigtap_final.ljust(10),
                'prd_cnspac': cnspac, 'prd_sexo': sexo, 'prd_ibge': cod_ibge_paciente,
                'prd_cid': cid, 'prd_ldade': idade_str, 'prd_qt': quantidade_final,
                'prd_caten': '01', 'prd_naut': ' ' * 13, 'prd_org': 'BPA',
                'prd_nmpac': nome_paciente, 'prd_dtnasc': data_nasc_str,
                'prd_raca': raca, 'prd_etnia': etnia, 'prd_nac': '010',
                'prd_srv': str(servico_val).zfill(3) if servico_val else '   ',
                'prd_clf': str(classificacao_val).zfill(3) if classificacao_val else '   ',
                'prd_equipe_Seq': ' ' * 8, 'prd_equipe_Area': ' ' * 4,
                'prd_cnpj': ' ' * 14,
                'prd_cep_pcnte': str(reg_data.get('vcp_cep') or '').ljust(8),
                'prd_lograd_pcnte': codigo_logradouro.zfill(3),
                'prd_end_pcnte': str(reg_data.get('vcp_logradouro') or '').ljust(30),
                'prd_compl_pcnte': ' ' * 10,
                'prd_num_pcnte': numero,
                'prd_bairro_pcnte': str(reg_data.get('vcp_bairro_inicial') or '').ljust(30),
                'prd_ddtel_pcnte': ' ' * 11, 'prd_email_pcnte': ' ' * 40,
                'prd_ine': self.config.get('default_ine').ljust(10),
                'prd_cpf_pcnte': ' ' * 11, 'prd_situacao_rua': ' ',
                '_id_lancamento_original': reg_data.get('id_lancamento'),
                '_nm_profissional': nome_profissional_val,
                '_data_nasc_obj': data_nasc_obj
            }
            registros_bpa_i_sem_numeracao.append(registro_bpa_i)
        return registros_bpa_i_sem_numeracao
    
    def aplicar_deduplicacao(self, registros_brutos, metodo):
        if metodo == "por_id_lancamento":
            return self.deduplicate_por_id_lancamento_original(registros_brutos)
        return registros_brutos

    def aplicar_verificacao_idade_procedimento(self, registros_processados):
        self._log_message_gui("Aplicando regra de verificação de idade nos registros deduplicados...")
        registros_ajustados = []
        
        contador_alteracoes = 0

        for registro in registros_processados:
            registro_copia = registro.copy()
            cod_proc_sigtap = registro_copia.get('prd_pa', '').strip()
            data_nasc_obj = registro_copia.get('_data_nasc_obj')

            if cod_proc_sigtap == '0301070300' and data_nasc_obj:
                idade_paciente = self.calcular_idade(data_nasc_obj)
                if idade_paciente < 18:
                    self._log_message_gui(f"REGRA PÓS-DEDUPLICAÇÃO: Paciente com {idade_paciente} anos. Procedimento '0301070300' alterado para '0301010048'.")
                    registro_copia['prd_pa'] = '0301010048'.ljust(10)
                    
                    contador_alteracoes += 1

            registros_ajustados.append(registro_copia)
        
        self._log_message_gui(f"Verificação de idade concluída. Total de {contador_alteracoes} registros alterados (de '0301070300' para '0301010048').")
        return registros_ajustados


    def deduplicate_por_id_lancamento_original(self, registros_processados):
        self._log_message_gui(f"Iniciando deduplicação de {len(registros_processados)} registros...")
        if not registros_processados: return []
        ids_vistos = set()
        registros_finais = []
        for registro in registros_processados:
            id_original = registro.get('_id_lancamento_original')
            if id_original is not None and id_original not in ids_vistos:
                ids_vistos.add(id_original)
                registros_finais.append(registro)
        self._log_message_gui(f"Deduplicação concluída: {len(registros_finais)} registros únicos.")
        return registros_finais

    def _atribuir_folha_sequencia_final(self, lista_registros_processados):
        if not lista_registros_processados: return []
        lista_registros_processados.sort(key=lambda r: (r.get('prd_cnsmed', ''), r.get('prd_dtaten', '')))
        cns_atual, folha_atual, seq_atual = None, 0, 0
        registros_numerados = []
        for registro in lista_registros_processados:
            if registro.get('prd_cnsmed') != cns_atual:
                cns_atual = registro.get('prd_cnsmed')
                folha_atual += 1
                seq_atual = 1
            else:
                seq_atual += 1
                if seq_atual > 99:
                    folha_atual += 1
                    seq_atual = 1
            registro_copia = registro.copy()
            registro_copia['prd_flh'] = str(folha_atual).zfill(3)
            registro_copia['prd_seq'] = str(seq_atual).zfill(2)
            registros_numerados.append(registro_copia)
        return registros_numerados

    def gerar_arquivo_txt(self, competencia, registros_bpa, caminho_arquivo_base):
        if not registros_bpa: return False
        try:
            num_linhas = len(registros_bpa)
            num_folhas = 0
            if registros_bpa:
                num_folhas = int(registros_bpa[-1]['prd_flh'])

            campo_controle = 1111 

            header_dict = {
                'cbc_hdr_1': '01', 'cbc_hdr_2': '#BPA#', 'cbc_mvm': competencia,
                'cbc_lin': str(num_linhas).zfill(6), 'cbc_flh': str(num_folhas).zfill(6),
                'cbc_smt_vrf': str(campo_controle).zfill(4),
                'cbc_rsp': self.config.get('orgao_responsavel', '').ljust(30),
                'cbc_sgl': self.config.get('sigla_orgao', '').ljust(6),
                'cbc_cgccpf': self.config.get('cgc_cpf', '').zfill(14),
                'cbc_dst': self.config.get('orgao_destino', '').ljust(40),
                'cbc_dst_in': self.config.get('indicador_destino', 'M'),
                'cbc_versao': self.config.get('versao_sistema', '').ljust(10),
            }
            
            ordem_campos_bpa_i = [
                'prd_ident', 'prd_cnes', 'prd_cmp', 'prd_cnsmed', 'prd_cbo', 'prd_dtaten', 
                'prd_flh', 'prd_seq', 'prd_pa', 'prd_cnspac', 'prd_sexo', 'prd_ibge', 
                'prd_cid', 'prd_ldade', 'prd_qt', 'prd_caten', 'prd_naut', 'prd_org', 
                'prd_nmpac', 'prd_dtnasc', 'prd_raca', 'prd_etnia', 'prd_nac', 'prd_srv', 
                'prd_clf', 'prd_equipe_Seq', 'prd_equipe_Area', 'prd_cnpj', 'prd_cep_pcnte',
                'prd_lograd_pcnte', 'prd_end_pcnte', 'prd_compl_pcnte', 'prd_num_pcnte',
                'prd_bairro_pcnte', 'prd_ddtel_pcnte', 'prd_email_pcnte', 'prd_ine',
                'prd_cpf_pcnte', 'prd_situacao_rua'
            ]

            with open(caminho_arquivo_base, 'w', newline='', encoding='latin-1') as f:
                linha_header_str = "".join(header_dict.values())
                f.write(linha_header_str + '\r\n')
                for reg_dict in registros_bpa:
                    valores_ordenados = [str(reg_dict.get(k, '')) for k in ordem_campos_bpa_i]
                    linha_reg_str = "".join(valores_ordenados)
                    
                    f.write(linha_reg_str.ljust(350)[:350] + '\r\n')
            return True
        except Exception as e:
            self._log_message_gui(f"Erro ao gerar arquivo TXT: {e}")
            return False
        
    def _escrever_log_mapeamentos_faltantes(self):
        if not self.mapeamentos_faltantes_log: return
        nome_arquivo_log = "mapeamentos_procedimentos_faltantes.txt"
        try:
            with open(nome_arquivo_log, 'w', encoding='utf-8') as f:
                f.write(f"Relatório de Mapeamentos Faltantes (gerado em: {datetime.datetime.now():%Y-%m-%d %H:%M:%S})\n")
                f.write("="*80 + "\n")
                for codigo_curto, id_bd in sorted(list(self.mapeamentos_faltantes_log)):
                    f.write(f"Código Curto: '{codigo_curto}' (do ID no BD: {id_bd}) precisa ser adicionado ao mapeamento.\n")
            self._log_message_gui(f"AVISO: Log de mapeamentos faltantes salvo em '{nome_arquivo_log}'.")
        except Exception as e:
            self._log_message_gui(f"ERRO ao escrever log de mapeamentos faltantes: {e}")

    def gerar_relatorio_excel(self, registros_finais, contadores_modalidade, caminho_arquivo):
        try:
            self._log_message_gui("Preparando dados para o relatório Excel...")
            df_final = pd.DataFrame(registros_finais)
            
            df_modalidade = pd.DataFrame(list(contadores_modalidade.items()), columns=['Modalidade', 'Nº de Atendimentos (Brutos)'])
            df_modalidade = df_modalidade[df_modalidade['Nº de Atendimentos (Brutos)'] > 0].sort_values(by='Nº de Atendimentos (Brutos)', ascending=False)
            
            if not df_final.empty:
                df_final['idade_num'] = pd.to_numeric(df_final['prd_ldade'])
                bins = [-1, 5, 12, 17, 29, 59, 150]
                labels = ['0-5 anos', '6-12 anos', '13-17 anos', '18-29 anos', '30-59 anos', '60+ anos']
                df_final['faixa_etaria'] = pd.cut(df_final['idade_num'], bins=bins, labels=labels, right=True)
                df_faixa_etaria = df_final['faixa_etaria'].value_counts().sort_index().reset_index()
                df_faixa_etaria.columns = ['Faixa Etária', 'Nº de Procedimentos']
                
                df_profissionais = pd.DataFrame(columns=['Profissional', 'Nº de Atendimentos'])
                if '_nm_profissional' in df_final.columns:
                        df_profissionais = df_final['_nm_profissional'].value_counts().nlargest(20).reset_index()
                        df_profissionais.columns = ['Profissional', 'Nº de Atendimentos']

                df_municipios = df_final['prd_ibge'].value_counts().nlargest(20).reset_index()
                df_municipios.columns = ['IBGE Município', 'Nº de Procedimentos']
            else:
                df_faixa_etaria = pd.DataFrame(columns=['Faixa Etária', 'Nº de Procedimentos'])
                df_profissionais = pd.DataFrame(columns=['Profissional', 'Nº de Atendimentos'])
                df_municipios = pd.DataFrame(columns=['IBGE Município', 'Nº de Procedimentos'])
            
            self._log_message_gui("Escrevendo arquivo Excel...")
            with pd.ExcelWriter(caminho_arquivo, engine='openpyxl') as writer:
                df_modalidade.to_excel(writer, sheet_name='Atendimentos por Modalidade', index=False)
                df_faixa_etaria.to_excel(writer, sheet_name='Atendimentos por Faixa Etária', index=False)
                df_profissionais.to_excel(writer, sheet_name='Top Profissionais', index=False)
                df_municipios.to_excel(writer, sheet_name='Top Municípios de Origem', index=False)
            return True, caminho_arquivo
        except Exception as e:
            self._log_message_gui(f"Erro ao gerar relatório Excel: {e}")
            import traceback; traceback.print_exc()
            return False, str(e)


class BPAExporterGUI:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Exportador BPA-I (SIGH Profissional)")
        self.root.geometry("1150x850")
        
        self.exporter = BPAExporter()
        self.db = Database()
        self.exporter.gui_log_callback = self._log_message

        style = ttk.Style()
        style.theme_use('clam')
        
        self.frame_conexao = ttk.LabelFrame(root_window, text="1. Conexão ao Banco de Dados")
        self.frame_conexao.pack(fill="x", padx=10, pady=5, ipady=5)
        self.frame_filtros = ttk.LabelFrame(root_window, text="2. Filtros e Deduplicação")
        self.frame_filtros.pack(fill="x", padx=10, pady=5, ipady=5)
        self.frame_config = ttk.LabelFrame(root_window, text="3. Configurações do Arquivo BPA-I")
        self.frame_config.pack(fill="x", padx=10, pady=5, ipady=5)
        self.frame_acoes = ttk.LabelFrame(root_window, text="4. Ações e Totais")
        self.frame_acoes.pack(fill="x", padx=10, pady=5, ipady=5)
        self.frame_log = ttk.LabelFrame(root_window, text="Log de Eventos")
        self.frame_log.pack(fill="both", expand=True, padx=10, pady=5)

        self._criar_widgets_conexao()
        self._criar_widgets_filtros()
        self._criar_widgets_config()
        self._criar_widgets_acoes()
        self._criar_widgets_log()

        self.registros_bpa_processados = []
        self.contadores_para_indicadores = {}
        self._log_message("Interface iniciada. Conecte-se ao banco de dados.")
    
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
        ttk.Label(self.frame_filtros, text="Data Início:").grid(row=0, column=0, padx=5, pady=3, sticky="w")
        self.data_inicio_entry = DateEntry(self.frame_filtros, width=12, date_pattern='dd/mm/yyyy')
        self.data_inicio_entry.grid(row=0, column=1, padx=5, pady=3, sticky="ew")
        ttk.Label(self.frame_filtros, text="Data Fim:").grid(row=0, column=2, padx=5, pady=3, sticky="w")
        self.data_fim_entry = DateEntry(self.frame_filtros, width=12, date_pattern='dd/mm/yyyy')
        self.data_fim_entry.grid(row=0, column=3, padx=5, pady=3, sticky="ew")
        ttk.Label(self.frame_filtros, text="Competência (AAAAMM):").grid(row=0, column=4, padx=5, pady=3, sticky="w")
        self.competencia_entry = ttk.Entry(self.frame_filtros, width=10)
        self.competencia_entry.insert(0, datetime.datetime.now().strftime("%Y%m"))
        self.competencia_entry.grid(row=0, column=5, padx=5, pady=3, sticky="ew")
        ttk.Label(self.frame_filtros, text="Critério de Data:").grid(row=1, column=0, padx=5, pady=3, sticky="w")
        self.criterio_data_combo = ttk.Combobox(self.frame_filtros, values=["Data do Lançamento (Recomendado)", "Competência da Conta"], width=30, state="readonly")
        self.criterio_data_combo.current(0)
        self.criterio_data_combo.grid(row=1, column=1, columnspan=3, padx=5, pady=3, sticky="ew")
        
        self.deduplicacao_var = tk.BooleanVar(value=True)
        self.chk_deduplicacao = ttk.Checkbutton(self.frame_filtros, text="Aplicar Deduplicação (Recomendado)", variable=self.deduplicacao_var)
        self.chk_deduplicacao.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")


    def _criar_widgets_config(self):
        bpa_config_fields = [ ("Órgão Responsável:", "orgao_resp_entry", self.exporter.config['orgao_responsavel'], 35), ("Sigla Órgão:", "sigla_orgao_entry", self.exporter.config['sigla_orgao'], 8), ("CNPJ/CPF Estab.:", "cgc_cpf_entry", self.exporter.config['cgc_cpf'], 18), ("Órgão Destino:", "orgao_destino_entry", self.exporter.config['orgao_destino'], 35), ("Indicador Destino (M/E):", "indicador_destino_combo", ["M", "E"], 5), ("Versão Sistema BPA:", "versao_sistema_entry", self.exporter.config['versao_sistema'], 10), ("CNES Estabelecimento:", "cnes_entry", self.exporter.config['cnes'], 10) ]
        for i, (label_text, attr_name, default_val, width) in enumerate(bpa_config_fields):
            row, col_offset = divmod(i, 2)
            ttk.Label(self.frame_config, text=label_text).grid(row=row, column=col_offset*2, padx=5, pady=3, sticky="w")
            if isinstance(default_val, list): combo = ttk.Combobox(self.frame_config, values=default_val, width=width, state="readonly"); combo.set(self.exporter.config['indicador_destino']); combo.grid(row=row, column=col_offset*2 + 1, padx=5, pady=3, sticky="ew"); setattr(self, attr_name, combo)
            else: entry = ttk.Entry(self.frame_config, width=width); entry.insert(0, default_val); entry.grid(row=row, column=col_offset*2 + 1, padx=5, pady=3, sticky="ew"); setattr(self, attr_name, entry)

    def _criar_widgets_acoes(self):
        self.btn_consultar_dados = ttk.Button(self.frame_acoes, text="Consultar Dados do BD", command=self.iniciar_consulta_dados, state="disabled")
        self.btn_consultar_dados.grid(row=0, column=0, padx=10, pady=10, ipady=5, sticky="ew")
        self.btn_exportar_txt = ttk.Button(self.frame_acoes, text="Exportar Arquivo BPA (.TXT)", command=self.exportar_arquivo_txt, state="disabled")
        self.btn_exportar_txt.grid(row=0, column=1, padx=10, pady=10, ipady=5, sticky="ew")
        self.btn_relatorio_producao = ttk.Button(self.frame_acoes, text="Gerar Relatório de Produção", command=self.gerar_relatorio_producao_handler, state="disabled")
        self.btn_relatorio_producao.grid(row=0, column=2, padx=10, pady=10, ipady=5, sticky="ew")
        
        frame_contadores = ttk.Frame(self.frame_acoes)
        frame_contadores.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")
        ttk.Label(frame_contadores, text="Lançamentos BPA:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.lbl_total_bpa_valor = ttk.Label(frame_contadores, text="0", font=('Helvetica', 10, 'bold'))
        self.lbl_total_bpa_valor.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        ttk.Label(frame_contadores, text="Lançamentos APAC (Ignorados):").grid(row=0, column=2, padx=5, pady=2, sticky="e")
        self.lbl_total_apac_valor = ttk.Label(frame_contadores, text="0", font=('Helvetica', 10, 'bold'))
        self.lbl_total_apac_valor.grid(row=0, column=3, padx=5, pady=2, sticky="w")
        ttk.Label(frame_contadores, text="Registros Finais para Exportar:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.lbl_total_registros_valor = ttk.Label(frame_contadores, text="0", font=('Helvetica', 10, 'bold'))
        self.lbl_total_registros_valor.grid(row=1, column=1, padx=5, pady=2, sticky="w")

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
        db_params = { "db_name": self.db_name.get(), "user": self.db_user.get(), "password": self.db_password.get(), "host": self.db_host.get(), "port": self.db_port.get() }
        sucesso, mensagem = self.db.conectar(**db_params)
        if sucesso:
            self._log_message("Conexão com o banco de dados estabelecida com sucesso!")
            self.exporter.conn = self.db.conn
            messagebox.showinfo("Sucesso", "Conexão estabelecida!")
            self.btn_consultar_dados.config(state="normal")
        else:
            self._log_message(f"Falha ao conectar ao banco: {mensagem}")
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar.\n\nDetalhe: {mensagem}")
    
    def _atualizar_config_exporter(self):
        self.exporter.config['orgao_responsavel'] = self.orgao_resp_entry.get()
        self.exporter.config['sigla_orgao'] = self.sigla_orgao_entry.get()
        self.exporter.config['cgc_cpf'] = self.cgc_cpf_entry.get()
        self.exporter.config['orgao_destino'] = self.orgao_destino_entry.get()
        self.exporter.config['indicador_destino'] = self.indicador_destino_combo.get()
        self.exporter.config['versao_sistema'] = self.versao_sistema_entry.get()
        self.exporter.config['cnes'] = self.cnes_entry.get()

    def iniciar_consulta_dados(self):
        self.btn_consultar_dados.config(state="disabled")
        self.btn_exportar_txt.config(state="disabled")
        if hasattr(self, 'btn_relatorio_producao'): self.btn_relatorio_producao.config(state="disabled")

        try:
            data_inicio_val = self.data_inicio_entry.get_date()
            data_fim_val = self.data_fim_entry.get_date()
            competencia_val = self.competencia_entry.get()
            
            map_criterio = {"Data do Lançamento (Recomendado)": "lancamento", "Competência da Conta": "competencia"}
            criterio_interno = map_criterio.get(self.criterio_data_combo.get())
            
            aplicar_dedup = self.deduplicacao_var.get()
            
            self._atualizar_config_exporter()

            registros_processados_sem_num, contadores, total_apac = self.exporter.consultar_dados_completo(
                data_inicio_val, data_fim_val, competencia_val, criterio_interno
            )
            
            self.contadores_para_indicadores = contadores
            self.lbl_total_bpa_valor.config(text=str(len(registros_processados_sem_num)))
            self.lbl_total_apac_valor.config(text=str(total_apac))
            
            if registros_processados_sem_num:
                
                registros_para_processamento_final = registros_processados_sem_num
                if aplicar_dedup:
                    self._log_message("Aplicando deduplicação...")
                    registros_para_processamento_final = self.exporter.deduplicate_por_id_lancamento_original(registros_processados_sem_num)
                else:
                    self._log_message("AVISO: Deduplicação desativada. Todos os registros brutos (pós-filtro APAC) serão processados.")

                registros_verificados = self.exporter.aplicar_verificacao_idade_procedimento(registros_para_processamento_final)

                self.registros_bpa_processados = self.exporter._atribuir_folha_sequencia_final(registros_verificados)
                
                self.lbl_total_registros_valor.config(text=str(len(self.registros_bpa_processados)))
                
                self.btn_exportar_txt.config(state="normal")
                if hasattr(self, 'btn_relatorio_producao'): self.btn_relatorio_producao.config(state="normal")
            else:
                self.registros_bpa_processados = []
                self.contadores_para_indicadores = {}
                self.lbl_total_registros_valor.config(text="0")
        finally:
            self.btn_consultar_dados.config(state="normal")

    def gerar_relatorio_producao_handler(self):
        if not self.registros_bpa_processados:
            messagebox.showwarning("Sem Dados", "É necessário realizar uma consulta bem-sucedida primeiro.")
            return
        caminho_arquivo = filedialog.asksaveasfilename(
            initialfile=f"Relatorio_Producao_{self.competencia_entry.get()}.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Arquivos Excel", "*.xlsx")],
            title="Salvar Relatório de Produção"
        )
        if not caminho_arquivo: return
        self._log_message("Gerando relatório de produção em Excel...")
        sucesso, resultado = self.exporter.gerar_relatorio_excel(
            self.registros_bpa_processados, 
            self.contadores_para_indicadores,
            caminho_arquivo
        )
        if sucesso:
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso: {resultado}")
        else:
            messagebox.showerror("Erro", f"Falha ao gerar relatório: {resultado}")

    def exportar_arquivo_txt(self):
        if not self.registros_bpa_processados:
            messagebox.showwarning("Sem Dados", "Não há dados para exportar.")
            return
        competencia_val = self.competencia_entry.get()
        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt")],
            title="Salvar Arquivo BPA"
        )
        if not caminho_arquivo: return
        self._atualizar_config_exporter()
        sucesso = self.exporter.gerar_arquivo_txt(competencia_val, self.registros_bpa_processados, caminho_arquivo)
        if sucesso:
            messagebox.showinfo("Sucesso", f"Arquivo BPA gerado em: {caminho_arquivo}")
        else:
            messagebox.showerror("Erro", "Falha ao gerar o arquivo TXT.")


def main():
    root = tk.Tk()
    app = BPAExporterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()