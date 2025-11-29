# shared/mapeamento_procedimentos.py

def carregar_tabela_procedimentos_cid():
    """
    Carrega a tabela de correspondência entre os códigos curtos internos e os dados do SIGTAP.
    Cada procedimento é classificado como BPA ou APAC e associado a uma modalidade de reabilitação.
    """
    tabela = {}

    def adicionar_procedimento(codigo, detalhes, modalidade):
        # Define a categoria (BPA/APAC) e a modalidade para cada procedimento
        detalhes['categoria'] = 'APAC' if modalidade == 'APAC' else 'BPA'
        detalhes['modalidade'] = modalidade
        tabela[str(codigo)] = detalhes

    # --- INÍCIO DOS MAPEAMENTOS DE PROCEDIMENTOS ---

    # REABILITAÇÃO FÍSICA
    modalidade_fisica = 'Reabilitação Física'
    adicionar_procedimento('14', {'codigo_sigtap': '0302060014', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'G968', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('15', {'codigo_sigtap': '0211030015', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_fisica)
    adicionar_procedimento('19', {'codigo_sigtap': '0302050019', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'M968', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('22', {'codigo_sigtap': '0302060022', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'M968', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('23', {'codigo_sigtap': '0211030023', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_fisica)
    adicionar_procedimento('27', {'codigo_sigtap': '0302050027', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'M998', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('29', {'codigo_sigtap': '0301070229', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'U099', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('30', {'codigo_sigtap': '0302060030', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'G839', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('31', {'codigo_sigtap': '0211030031', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_fisica)
    adicionar_procedimento('45', {'codigo_sigtap': '0701010045', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'R268', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('49', {'codigo_sigtap': '0302060049', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'F849', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('56', {'codigo_sigtap': '0302040056', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'I988', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('57', {'codigo_sigtap': '0302060057', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'Q878', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('63', {'codigo_sigtap': '0301100063', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_fisica)
    adicionar_procedimento('74', {'codigo_sigtap': '0211030074', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'M797', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('105', {'codigo_sigtap': '0301070105', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'M638', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('118', {'codigo_sigtap': '0701010118', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'R268', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('121', {'codigo_sigtap': '0301070121', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'G979', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('129', {'codigo_sigtap': '0701010029', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'R268', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('134', {'codigo_sigtap': '0701010134', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'R268', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('172', {'codigo_sigtap': '0701020172', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'G838', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('180', {'codigo_sigtap': '0301080160', 'servico': '164', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_fisica)
    adicionar_procedimento('210', {'codigo_sigtap': '0301070210', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_fisica)
    adicionar_procedimento('229', {'codigo_sigtap': '0701020229', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'Q898', 'cid_obrigatorio': False}, modalidade_fisica)
    adicionar_procedimento('237', {'codigo_sigtap': '0301070237', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_fisica)
    adicionar_procedimento('340', {'codigo_sigtap': '0211030040', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_fisica)
    adicionar_procedimento('530', {'codigo_sigtap': '0309050030', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_fisica)
    adicionar_procedimento('1105', {'codigo_sigtap': '0701020105', 'servico': '135', 'classificacao': '003', 'cid_sugestao': 'G728', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('2210', {'codigo_sigtap': '0701020210', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'G718', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('2237', {'codigo_sigtap': '0701020237', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'G718', 'cid_obrigatorio': True}, modalidade_fisica)
    adicionar_procedimento('2245', {'codigo_sigtap': '0701020229', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'G718', 'cid_obrigatorio': True}, modalidade_fisica)

    # REABILITAÇÃO INTELECTUAL
    modalidade_intelectual = 'Reabilitação Intelectual'
    adicionar_procedimento('13', {'codigo_sigtap': '0211100013', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_intelectual)
    adicionar_procedimento('40', {'codigo_sigtap': '0301070040', 'servico': '135', 'classificacao': '002', 'cid_sugestao': 'F840', 'cid_obrigatorio': True}, modalidade_intelectual)
    adicionar_procedimento('59', {'codigo_sigtap': '0301070059', 'servico': '135', 'classificacao': '002', 'cid_sugestao': 'F840', 'cid_obrigatorio': True}, modalidade_intelectual)
    adicionar_procedimento('67', {'codigo_sigtap': '0301070067', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_intelectual)
    adicionar_procedimento('75', {'codigo_sigtap': '0301070075', 'servico': '135', 'classificacao': '002', 'cid_sugestao': 'F83', 'cid_obrigatorio': False}, modalidade_intelectual)
    adicionar_procedimento('113', {'codigo_sigtap': '0301070113', 'servico': '135', 'classificacao': '002', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_intelectual)
    adicionar_procedimento('124', {'codigo_sigtap': '0301070024', 'servico': '135', 'classificacao': '002', 'cid_sugestao': 'F840', 'cid_obrigatorio': True}, modalidade_intelectual)
    adicionar_procedimento('261', {'codigo_sigtap': '0301070261', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_intelectual)
    adicionar_procedimento('296', {'codigo_sigtap': '0301070296', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_intelectual)
    adicionar_procedimento('300', {'codigo_sigtap': '0301070300', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_intelectual)

    # REABILITAÇÃO VISUAL
    modalidade_visual = 'Reabilitação Visual'
    adicionar_procedimento('18', {'codigo_sigtap': '0302030018', 'servico': '135', 'classificacao': '001', 'cid_sugestao': 'H542', 'cid_obrigatorio': True}, modalidade_visual)
    adicionar_procedimento('20', {'codigo_sigtap': '0211060020', 'servico': '135', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_visual)
    adicionar_procedimento('38', {'codigo_sigtap': '0211060038', 'servico': '131', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_visual)
    adicionar_procedimento('54', {'codigo_sigtap': '0211060054', 'servico': '135', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_visual)
    adicionar_procedimento('100', {'codigo_sigtap': '0211060100', 'servico': '135', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_visual)
    adicionar_procedimento('148', {'codigo_sigtap': '0301070148', 'servico': '135', 'classificacao': '001', 'cid_sugestao': 'H540', 'cid_obrigatorio': True}, modalidade_visual)
    adicionar_procedimento('151', {'codigo_sigtap': '0211060151', 'servico': '135', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_visual)
    adicionar_procedimento('156', {'codigo_sigtap': '0301070156', 'servico': '135', 'classificacao': '001', 'cid_sugestao': 'H542', 'cid_obrigatorio': True}, modalidade_visual)
    adicionar_procedimento('164', {'codigo_sigtap': '0301070164', 'servico': '135', 'classificacao': '001', 'cid_sugestao': 'H542', 'cid_obrigatorio': True}, modalidade_visual)
    adicionar_procedimento('224', {'codigo_sigtap': '0211060224', 'servico': '135', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_visual)
    adicionar_procedimento('232', {'codigo_sigtap': '0211060232', 'servico': '135', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_visual)
    adicionar_procedimento('245', {'codigo_sigtap': '0301070245', 'servico': '135', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_visual)
    adicionar_procedimento('259', {'codigo_sigtap': '0211060259', 'servico': '135', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_visual)
    adicionar_procedimento('1127', {'codigo_sigtap': '0211060127', 'servico': '135', 'classificacao': '001', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_visual)

    # REABILITAÇÃO AUDITIVA
    modalidade_auditiva = 'Reabilitação Auditiva'
    adicionar_procedimento('25', {'codigo_sigtap': '0211070025', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('26', {'codigo_sigtap': '0302030026', 'servico': '135', 'classificacao': '001', 'cid_sugestao': 'H519', 'cid_obrigatorio': True}, modalidade_auditiva)
    adicionar_procedimento('33', {'codigo_sigtap': '0211070033', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('41', {'codigo_sigtap': '0211070041', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('50', {'codigo_sigtap': '0211070050', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('68', {'codigo_sigtap': '0211070068', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('76', {'codigo_sigtap': '0211070076', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('84', {'codigo_sigtap': '0211070084', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('114', {'codigo_sigtap': '0211070114', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('149', {'codigo_sigtap': '0211070149', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('157', {'codigo_sigtap': '0211070157', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('203', {'codigo_sigtap': '0211070203', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('211', {'codigo_sigtap': '0211070211', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('246', {'codigo_sigtap': '0211070246', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('253', {'codigo_sigtap': '0301070253', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('262', {'codigo_sigtap': '0211070262', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('270', {'codigo_sigtap': '0211070270', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('338', {'codigo_sigtap': '0701030038', 'servico': '135', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_auditiva)
    adicionar_procedimento('354', {'codigo_sigtap': '0701030054', 'servico': '135', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_auditiva)
    adicionar_procedimento('1113', {'codigo_sigtap': '0211050113', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('7424', {'codigo_sigtap': '0211070424', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)
    adicionar_procedimento('7432', {'codigo_sigtap': '0211070432', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_auditiva)

    # OSTOMIZADOS
    modalidade_ostomizados = 'Ostomizados'
    adicionar_procedimento('512', {'codigo_sigtap': '0701050012', 'servico': '135', 'classificacao': '012', 'cid_sugestao': 'Z933', 'cid_obrigatorio': True}, modalidade_ostomizados)
    adicionar_procedimento('520', {'codigo_sigtap': '0701050020', 'servico': '135', 'classificacao': '012', 'cid_sugestao': 'Z933', 'cid_obrigatorio': True}, modalidade_ostomizados)

    # ÁREA COMUM
    modalidade_comum = 'Área Comum'
    adicionar_procedimento('28', {'codigo_sigtap': '0101010028', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('36', {'codigo_sigtap': '0301040036', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('39', {'codigo_sigtap': '0301100039', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('44', {'codigo_sigtap': '0301040044', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('48', {'codigo_sigtap': '0301010048', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('72', {'codigo_sigtap': '0301010072', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('79', {'codigo_sigtap': '0301040079', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('95', {'codigo_sigtap': '0301040095', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('160', {'codigo_sigtap': '0301080160', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('173', {'codigo_sigtap': '0211070173', 'servico': '135', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('276', {'codigo_sigtap': '0301100276', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('284', {'codigo_sigtap': '0301100284', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('288', {'codigo_sigtap': '0301070288', 'servico': '135', 'classificacao': '002', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)
    adicionar_procedimento('424', {'codigo_sigtap': '0101040024', 'servico': '135', 'classificacao': '003', 'cid_sugestao': '', 'cid_obrigatorio': False}, modalidade_comum)

    # APACS (procedimentos que não devem ir para o BPA)
    modalidade_apac = 'APAC'
    adicionar_procedimento('32', {'codigo_sigtap': '0301070032', 'servico': '135', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('37', {'codigo_sigtap': '0701010240', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'G969', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('46', {'codigo_sigtap': '0701030046', 'servico': '164', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('62', {'codigo_sigtap': '0701030062', 'servico': '164', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('70', {'codigo_sigtap': '0701030070', 'servico': '164', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('89', {'codigo_sigtap': '0701030089', 'servico': '164', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('92', {'codigo_sigtap': '0211070092', 'servico': '135', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('106', {'codigo_sigtap': '0211070106', 'servico': '135', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('127', {'codigo_sigtap': '0701030127', 'servico': '164', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('135', {'codigo_sigtap': '0701030135', 'servico': '164', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('143', {'codigo_sigtap': '0701030143', 'servico': '164', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('207', {'codigo_sigtap': '0701010207', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'G969', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('215', {'codigo_sigtap': '0701010215', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'G969', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('223', {'codigo_sigtap': '0701010223', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'G128', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('231', {'codigo_sigtap': '0701010231', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'Q748', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('240', {'codigo_sigtap': '0701010240', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'G969', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('258', {'codigo_sigtap': '0701010258', 'servico': '164', 'classificacao': '001', 'cid_sugestao': 'G969', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('319', {'codigo_sigtap': '0211070319', 'servico': '135', 'classificacao': '005', 'cid_sugestao': 'H919', 'cid_obrigatorio': True}, modalidade_apac)
    adicionar_procedimento('1151', {'codigo_sigtap': '0701030151', 'servico': '164', 'classificacao': '005', 'cid_sugestao': '', 'cid_obrigatorio': True}, modalidade_apac)

    return tabela