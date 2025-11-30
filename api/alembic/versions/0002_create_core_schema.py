"""Create core schema for indicators and exportadores"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_create_core_schema"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    # Schemas
    op.execute("CREATE SCHEMA IF NOT EXISTS sigh")
    op.execute("CREATE SCHEMA IF NOT EXISTS endereco_sigh")
    op.execute("CREATE SCHEMA IF NOT EXISTS aihu")

    # endereco_sigh.municipios
    op.create_table(
        "municipios",
        sa.Column("id_municipio", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("cod_ibge", sa.String(length=6), nullable=False),
        sa.Column("nome", sa.String(length=255), nullable=False),
        sa.Column("uf", sa.String(length=2), nullable=False),
        sa.UniqueConstraint("cod_ibge"),
        schema="endereco_sigh",
        comment="Municipios para referencia territorial",
    )

    # endereco_sigh.logradouros
    op.create_table(
        "logradouros",
        sa.Column("id_logradouro", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("tp_logradouro", sa.String(length=20), nullable=True),
        sa.Column("logradouro", sa.String(length=255), nullable=False),
        sa.Column("cep", sa.String(length=8), nullable=True),
        sa.Column("bairro_inicial", sa.String(length=255), nullable=True),
        sa.Column("cod_municipio", sa.BigInteger(), sa.ForeignKey("endereco_sigh.municipios.id_municipio"), nullable=True),
        schema="endereco_sigh",
        comment="Logradouros (enderecos) com municipio",
    )

    # aihu.ceps_municipios_ibges
    op.create_table(
        "ceps_municipios_ibges",
        sa.Column("cep", sa.String(length=8), primary_key=True),
        sa.Column("ibge", sa.String(length=6), nullable=False),
        schema="aihu",
        comment="Mapeamento CEP -> IBGE (simplificado)",
    )

    # sigh tables
    op.create_table(
        "pacientes",
        sa.Column("id_paciente", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("nm_paciente", sa.String(length=255), nullable=False),
        sa.Column("data_nasc", sa.Date(), nullable=True),
        sa.Column("cod_sexo", sa.String(length=1), nullable=True),
        sa.Column("cod_raca_etnia", sa.String(length=2), nullable=True),
        sa.Column("cod_etnia_indigena", sa.String(length=4), nullable=True),
        sa.Column("cod_nacionalidade", sa.String(length=3), nullable=True),
        sa.Column("cns", sa.String(length=15), nullable=True),
        sa.Column("cpf", sa.String(length=14), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="sigh",
        comment="Pacientes atendidos (basico para indicadores e exportadores)",
    )

    op.create_table(
        "ficha_amb_int",
        sa.Column("id_fia", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("cod_paciente", sa.BigInteger(), sa.ForeignKey("sigh.pacientes.id_paciente"), nullable=False),
        sa.Column("diagnostico", sa.String(length=10), nullable=True),
        sa.Column("matricula", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="sigh",
        comment="Ficha de atendimento ambulatorial/internacao",
    )

    op.create_table(
        "prestadores",
        sa.Column("id_prestador", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("nm_prestador", sa.String(length=255), nullable=False),
        sa.Column("cns", sa.String(length=15), nullable=True),
        sa.Column("cnpj", sa.String(length=14), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="sigh",
        comment="Prestadores de servico de saude",
    )

    op.create_table(
        "procedimentos",
        sa.Column("id_procedimento", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("codigo_procedimento", sa.String(length=10), nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=True),
        sa.UniqueConstraint("codigo_procedimento"),
        schema="sigh",
        comment="Procedimentos cadastrais (codigo curto e SIGTAP)",
    )

    op.create_table(
        "cids",
        sa.Column("id_cid", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("codigo", sa.String(length=10), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("codigo"),
        schema="sigh",
        comment="Tabela de codigos CID",
    )

    op.create_table(
        "contas",
        sa.Column("id_conta", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("cod_fia", sa.BigInteger(), sa.ForeignKey("sigh.ficha_amb_int.id_fia"), nullable=False),
        sa.Column("competencia", sa.String(length=7), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("status_conta", sa.String(length=1), nullable=False, server_default="A"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="sigh",
        comment="Contas de atendimento/competencia",
    )

    op.create_table(
        "v_cons_prestadores_cbos_scola",
        sa.Column("id_prestador", sa.BigInteger(), sa.ForeignKey("sigh.prestadores.id_prestador"), primary_key=True),
        sa.Column("codigo_cbo", sa.String(length=6), nullable=True),
        schema="sigh",
        comment="Tabela de apoio para CBO por prestador",
    )

    op.create_table(
        "v_cons_racas_etnias_scola",
        sa.Column("id_raca_etnia", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("codigo_raca_etnia", sa.String(length=2), nullable=False),
        schema="sigh",
        comment="Tabela de apoio para racas/etnias",
    )

    op.create_table(
        "v_cons_pacientes_laboratorios",
        sa.Column("registro", sa.BigInteger(), primary_key=True),
        sa.Column("mae", sa.String(length=255), nullable=True),
        sa.Column("cartao_sus", sa.String(length=15), nullable=True),
        schema="sigh",
        comment="Tabela de apoio para pacientes (nome da mae/cartao SUS)",
    )

    op.create_table(
        "cids_fia",
        sa.Column("id_cid_fia", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("cod_fia", sa.BigInteger(), sa.ForeignKey("sigh.ficha_amb_int.id_fia"), nullable=False),
        sa.Column("cod_cid_fia", sa.BigInteger(), sa.ForeignKey("sigh.cids.id_cid"), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        schema="sigh",
        comment="CID principal por ficha",
    )

    op.create_table(
        "enderecos",
        sa.Column("id_endereco", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("cod_paciente", sa.BigInteger(), sa.ForeignKey("sigh.pacientes.id_paciente"), nullable=False),
        sa.Column("cod_logradouro", sa.BigInteger(), sa.ForeignKey("endereco_sigh.logradouros.id_logradouro"), nullable=True),
        sa.Column("numero", sa.String(length=10), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("data_hora_atualizacao", sa.DateTime(timezone=True), nullable=True),
        sa.Column("data_hora_criacao", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="sigh",
        comment="Enderecos de pacientes",
    )

    op.create_table(
        "lancamentos",
        sa.Column("id_lancamento", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("cod_conta", sa.BigInteger(), sa.ForeignKey("sigh.contas.id_conta"), nullable=False),
        sa.Column("cod_proc", sa.BigInteger(), sa.ForeignKey("sigh.procedimentos.id_procedimento"), nullable=True),
        sa.Column("quantidade", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("cod_cid", sa.String(length=10), nullable=True),
        sa.Column("cod_serv", sa.String(length=10), nullable=True),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("cod_prestador", sa.BigInteger(), sa.ForeignKey("sigh.prestadores.id_prestador"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema="sigh",
        comment="Lancamentos de atendimentos para faturamento/indicadores",
    )

    # Seeds opcionais simples
    op.bulk_insert(
        sa.table(
            "procedimentos",
            sa.column("id_procedimento", sa.BigInteger()),
            sa.column("codigo_procedimento", sa.String()),
            sa.column("descricao", sa.String()),
        ),
        [
            {"id_procedimento": 1, "codigo_procedimento": "0301010048", "descricao": "Consulta"},
            {"id_procedimento": 2, "codigo_procedimento": "0301070075", "descricao": "Outro procedimento"},
        ],
        multiinsert=False,
    )


def downgrade():
    op.drop_table("lancamentos", schema="sigh")
    op.drop_table("enderecos", schema="sigh")
    op.drop_table("cids_fia", schema="sigh")
    op.drop_table("v_cons_pacientes_laboratorios", schema="sigh")
    op.drop_table("v_cons_racas_etnias_scola", schema="sigh")
    op.drop_table("v_cons_prestadores_cbos_scola", schema="sigh")
    op.drop_table("contas", schema="sigh")
    op.drop_table("cids", schema="sigh")
    op.drop_table("procedimentos", schema="sigh")
    op.drop_table("prestadores", schema="sigh")
    op.drop_table("ficha_amb_int", schema="sigh")
    op.drop_table("pacientes", schema="sigh")
    op.drop_table("logradouros", schema="endereco_sigh")
    op.drop_table("municipios", schema="endereco_sigh")
    op.drop_table("ceps_municipios_ibges", schema="aihu")
    op.execute("DROP SCHEMA IF EXISTS sigh CASCADE")
    op.execute("DROP SCHEMA IF EXISTS endereco_sigh CASCADE")
    op.execute("DROP SCHEMA IF EXISTS aihu CASCADE")
