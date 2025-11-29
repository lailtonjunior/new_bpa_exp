# shared/mapeamento_profissionais.py

def carregar_mapeamento_profissionais():
    """
    Retorna um dicionário que mapeia o ID do profissional (prestador)
    aos seus códigos padrão de serviço e classificação.
    Esta é a fonte de dados para o fallback quando um procedimento não
    possui serviço/classificação definidos.
    """
    mapeamento = {
        '16': {'servico': '135', 'classificacao': '002'}, '13': {'servico': '135', 'classificacao': '003'},
        '19': {'servico': '135', 'classificacao': '005'}, '10': {'servico': '135', 'classificacao': '002'},
        '20': {'servico': '135', 'classificacao': '003'}, '12': {'servico': '135', 'classificacao': '002'},
        '17': {'servico': '135', 'classificacao': '005'}, '26': {'servico': '135', 'classificacao': '002'},
        '31': {'servico': '135', 'classificacao': '003'}, '15': {'servico': '135', 'classificacao': '002'},
        '7': {'servico': '135', 'classificacao': '002'}, '28': {'servico': '135', 'classificacao': '005'},
        '9': {'servico': '135', 'classificacao': '002'}, '11': {'servico': '135', 'classificacao': '002'},
        '24': {'servico': '135', 'classificacao': '002'}, '5': {'servico': '135', 'classificacao': '002'},
        '29': {'servico': '135', 'classificacao': '002'}, '14': {'servico': '135', 'classificacao': '002'},
        '21': {'servico': '135', 'classificacao': '002'}, '3': {'servico': '135', 'classificacao': '002'},
        '43': {'servico': '135', 'classificacao': '002'}, '38': {'servico': '135', 'classificacao': '002'},
        '4': {'servico': '135', 'classificacao': '005'}, '22': {'servico': '135', 'classificacao': '002'},
        '46': {'servico': '135', 'classificacao': '002'}, '47': {'servico': '135', 'classificacao': '002'},
        '48': {'servico': '135', 'classificacao': '002'}, '49': {'servico': '135', 'classificacao': '003'},
        '52': {'servico': '135', 'classificacao': '003'}, '51': {'servico': '135', 'classificacao': '003'},
        '2': {'servico': '135', 'classificacao': '002'}, '53': {'servico': '135', 'classificacao': '003'},
        '55': {'servico': '135', 'classificacao': '003'}, '56': {'servico': '135', 'classificacao': '003'},
        '57': {'servico': '135', 'classificacao': '003'}, '58': {'servico': '135', 'classificacao': '001'},
        '59': {'servico': '135', 'classificacao': '003'}, '60': {'servico': '135', 'classificacao': '003'},
        '61': {'servico': '135', 'classificacao': '003'}, '62': {'servico': '135', 'classificacao': '003'},
        '63': {'servico': '135', 'classificacao': '003'}, '64': {'servico': '135', 'classificacao': '003'},
        '66': {'servico': '135', 'classificacao': '003'}, '68': {'servico': '135', 'classificacao': '001'},
        '71': {'servico': '135', 'classificacao': '003'}, '72': {'servico': '135', 'classificacao': '003'},
        '67': {'servico': '135', 'classificacao': '002'}, '40': {'servico': '135', 'classificacao': '002'},
        '41': {'servico': '135', 'classificacao': '002'}, '32': {'servico': '135', 'classificacao': '002'},
        '69': {'servico': '135', 'classificacao': '002'}, '18': {'servico': '135', 'classificacao': '002'},
        '8': {'servico': '135', 'classificacao': '002'}, '39': {'servico': '135', 'classificacao': '002'},
        '44': {'servico': '135', 'classificacao': '005'}, '54': {'servico': '135', 'classificacao': '003'},
        '73': {'servico': '135', 'classificacao': '002'}, '75': {'servico': '135', 'classificacao': '002'},
        '76': {'servico': '135', 'classificacao': '002'}, '34': {'servico': '135', 'classificacao': '003'},
        '78': {'servico': '135', 'classificacao': '002'}, '80': {'servico': '135', 'classificacao': '002'},
        '81': {'servico': '135', 'classificacao': '003'}, '33': {'servico': '135', 'classificacao': '005'},
        '83': {'servico': '135', 'classificacao': '002'}, '70': {'servico': '135', 'classificacao': '003'},
        '84': {'servico': '135', 'classificacao': '003'}, '85': {'servico': '135', 'classificacao': '002'},
        '35': {'servico': '135', 'classificacao': '002'}, '86': {'servico': '135', 'classificacao': '003'},
        '88': {'servico': '135', 'classificacao': '002'}, '89': {'servico': '135', 'classificacao': '003'},
        '87': {'servico': '135', 'classificacao': '003'}, '79': {'servico': '135', 'classificacao': '002'},
        '6': {'servico': '135', 'classificacao': '002'}, '94': {'servico': '135', 'classificacao': '002'}
    }
    return mapeamento