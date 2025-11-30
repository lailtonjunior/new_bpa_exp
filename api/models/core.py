import sqlalchemy as sa

from .base import Base, TimestampMixin


class Paciente(Base, TimestampMixin):
    __tablename__ = "pacientes"
    __table_args__ = {"schema": "sigh", "comment": "Pacientes atendidos (basico para indicadores e exportadores)"}

    id_paciente = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    nm_paciente = sa.Column(sa.String(255), nullable=False)
    data_nasc = sa.Column(sa.Date, nullable=True)
    cod_sexo = sa.Column(sa.String(1), nullable=True)
    cod_raca_etnia = sa.Column(sa.String(2), nullable=True)
    cod_etnia_indigena = sa.Column(sa.String(4), nullable=True)
    cod_nacionalidade = sa.Column(sa.String(3), nullable=True)
    cns = sa.Column(sa.String(15), nullable=True, unique=True)
    cpf = sa.Column(sa.String(14), nullable=True, unique=True)
    email = sa.Column(sa.String(255), nullable=True)


class FichaAmbInt(Base, TimestampMixin):
    __tablename__ = "ficha_amb_int"
    __table_args__ = {"schema": "sigh", "comment": "Ficha de atendimento ambulatorial/internacao"}

    id_fia = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    cod_paciente = sa.Column(sa.BigInteger, sa.ForeignKey("sigh.pacientes.id_paciente"), nullable=False)
    diagnostico = sa.Column(sa.String(10), nullable=True)
    matricula = sa.Column(sa.String(20), nullable=True)


class Conta(Base, TimestampMixin):
    __tablename__ = "contas"
    __table_args__ = {"schema": "sigh", "comment": "Contas de atendimento/competencia"}

    id_conta = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    cod_fia = sa.Column(sa.BigInteger, sa.ForeignKey("sigh.ficha_amb_int.id_fia"), nullable=False)
    competencia = sa.Column(sa.String(7), nullable=True)  # formato MM/YYYY
    ativo = sa.Column(sa.Boolean, default=True, nullable=False)
    status_conta = sa.Column(sa.String(1), default="A", nullable=False)


class Prestador(Base, TimestampMixin):
    __tablename__ = "prestadores"
    __table_args__ = {"schema": "sigh", "comment": "Prestadores de servico de saude"}

    id_prestador = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    nm_prestador = sa.Column(sa.String(255), nullable=False)
    cns = sa.Column(sa.String(15), nullable=True, unique=True)
    cnpj = sa.Column(sa.String(14), nullable=True)


class PrestadorCBO(Base):
    __tablename__ = "v_cons_prestadores_cbos_scola"
    __table_args__ = {"schema": "sigh", "comment": "Tabela de apoio para CBO por prestador"}

    id_prestador = sa.Column(sa.BigInteger, sa.ForeignKey("sigh.prestadores.id_prestador"), primary_key=True)
    codigo_cbo = sa.Column(sa.String(6), nullable=True)


class RacaEtnia(Base):
    __tablename__ = "v_cons_racas_etnias_scola"
    __table_args__ = {"schema": "sigh", "comment": "Tabela de apoio para racas/etnias"}

    id_raca_etnia = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    codigo_raca_etnia = sa.Column(sa.String(2), nullable=False)


class Procedimento(Base):
    __tablename__ = "procedimentos"
    __table_args__ = {"schema": "sigh", "comment": "Procedimentos cadastrais (codigo curto e SIGTAP)"}

    id_procedimento = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    codigo_procedimento = sa.Column(sa.String(10), nullable=False, unique=True)
    descricao = sa.Column(sa.String(255), nullable=True)


class CID(Base):
    __tablename__ = "cids"
    __table_args__ = {"schema": "sigh", "comment": "Tabela de codigos CID"}

    id_cid = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    codigo = sa.Column(sa.String(10), nullable=False, unique=True)
    ativo = sa.Column(sa.Boolean, default=True, nullable=False)


class CIDFIA(Base):
    __tablename__ = "cids_fia"
    __table_args__ = {"schema": "sigh", "comment": "CID principal por ficha"}

    id_cid_fia = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    cod_fia = sa.Column(sa.BigInteger, sa.ForeignKey("sigh.ficha_amb_int.id_fia"), nullable=False)
    cod_cid_fia = sa.Column(sa.BigInteger, sa.ForeignKey("sigh.cids.id_cid"), nullable=False)
    ordem = sa.Column(sa.Integer, default=1, nullable=False)
    ativo = sa.Column(sa.Boolean, default=True, nullable=False)


class Lancamento(Base, TimestampMixin):
    __tablename__ = "lancamentos"
    __table_args__ = {"schema": "sigh", "comment": "Lancamentos de atendimentos para faturamento/indicadores"}

    id_lancamento = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    cod_conta = sa.Column(sa.BigInteger, sa.ForeignKey("sigh.contas.id_conta"), nullable=False)
    cod_proc = sa.Column(sa.BigInteger, sa.ForeignKey("sigh.procedimentos.id_procedimento"), nullable=True)
    quantidade = sa.Column(sa.Integer, default=1, nullable=False)
    cod_cid = sa.Column(sa.String(10), nullable=True)
    cod_serv = sa.Column(sa.String(10), nullable=True)
    data = sa.Column(sa.Date, nullable=False)
    cod_prestador = sa.Column(sa.BigInteger, sa.ForeignKey("sigh.prestadores.id_prestador"), nullable=True)


class Endereco(Base, TimestampMixin):
    __tablename__ = "enderecos"
    __table_args__ = {"schema": "sigh", "comment": "Enderecos de pacientes"}

    id_endereco = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    cod_paciente = sa.Column(sa.BigInteger, sa.ForeignKey("sigh.pacientes.id_paciente"), nullable=False)
    cod_logradouro = sa.Column(sa.BigInteger, sa.ForeignKey("endereco_sigh.logradouros.id_logradouro"), nullable=True)
    numero = sa.Column(sa.String(10), nullable=True)
    ativo = sa.Column(sa.Boolean, default=True, nullable=False)
    data_hora_atualizacao = sa.Column(sa.DateTime(timezone=True), nullable=True)
    data_hora_criacao = sa.Column(sa.DateTime(timezone=True), nullable=True)


class Logradouro(Base):
    __tablename__ = "logradouros"
    __table_args__ = {"schema": "endereco_sigh", "comment": "Logradouros (enderecos) com municipio"}

    id_logradouro = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    tp_logradouro = sa.Column(sa.String(20), nullable=True)
    logradouro = sa.Column(sa.String(255), nullable=False)
    cep = sa.Column(sa.String(8), nullable=True)
    bairro_inicial = sa.Column(sa.String(255), nullable=True)
    cod_municipio = sa.Column(sa.BigInteger, sa.ForeignKey("endereco_sigh.municipios.id_municipio"), nullable=True)


class Municipio(Base):
    __tablename__ = "municipios"
    __table_args__ = (
        sa.UniqueConstraint("cod_ibge"),
        {"schema": "endereco_sigh", "comment": "Municipios para referencia territorial"},
    )

    id_municipio = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    cod_ibge = sa.Column(sa.String(6), nullable=False)
    nome = sa.Column(sa.String(255), nullable=False)
    uf = sa.Column(sa.String(2), nullable=False)


class CepMunicipio(Base):
    __tablename__ = "ceps_municipios_ibges"
    __table_args__ = {"schema": "aihu", "comment": "Mapeamento CEP -> IBGE (simplificado)"}

    cep = sa.Column(sa.String(8), primary_key=True)
    ibge = sa.Column(sa.String(6), nullable=False)


class PacienteLaboratorio(Base):
    __tablename__ = "v_cons_pacientes_laboratorios"
    __table_args__ = {"schema": "sigh", "comment": "Tabela de apoio para pacientes (nome da mae/cartao SUS)"}

    registro = sa.Column(sa.BigInteger, primary_key=True)
    mae = sa.Column(sa.String(255), nullable=True)
    cartao_sus = sa.Column(sa.String(15), nullable=True)
