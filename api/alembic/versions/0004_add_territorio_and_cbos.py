"""Add territorio coordinates and CBO descriptions"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0004_add_territorio_and_cbos"
down_revision = "0003_add_valor_procedimento"
branch_labels = None
depends_on = None


def upgrade():
    # Add lat/lon to municipios
    op.add_column("municipios", sa.Column("latitude", sa.Numeric(10, 6), nullable=True), schema="endereco_sigh")
    op.add_column("municipios", sa.Column("longitude", sa.Numeric(10, 6), nullable=True), schema="endereco_sigh")

    # Create cbos table
    op.create_table(
        "cbos",
        sa.Column("id_cbo", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("codigo", sa.String(length=6), nullable=False, unique=True),
        sa.Column("descricao", sa.String(length=255), nullable=False),
        schema="sigh",
        comment="Tabela de CBO para enriquecimento de produtividade",
    )

    # Seed minimal CBO descriptions
    op.execute("INSERT INTO sigh.cbos (codigo, descricao) VALUES ('225133', 'Medico Psiquiatra') ON CONFLICT DO NOTHING")
    op.execute("INSERT INTO sigh.cbos (codigo, descricao) VALUES ('225275', 'Fisioterapeuta') ON CONFLICT DO NOTHING")
    op.execute("INSERT INTO sigh.cbos (codigo, descricao) VALUES ('225260', 'Fonoaudiologo') ON CONFLICT DO NOTHING")
    op.execute("INSERT INTO sigh.cbos (codigo, descricao) VALUES ('2231', 'Profissional de Saude') ON CONFLICT DO NOTHING")

    # Seed sample municipio coords (pode ser complementado com carga externa)
    op.execute(
        """
        UPDATE endereco_sigh.municipios SET latitude=-10.18, longitude=-48.33 WHERE cod_ibge='1721000'; -- Palmas
        UPDATE endereco_sigh.municipios SET latitude=-7.19, longitude=-48.20 WHERE cod_ibge='1702109'; -- Araguaina
        UPDATE endereco_sigh.municipios SET latitude=-8.06, longitude=-48.47 WHERE cod_ibge='1705508'; -- Colinas do Tocantins
        UPDATE endereco_sigh.municipios SET latitude=-11.72, longitude=-49.06 WHERE cod_ibge='1709500'; -- Gurupi
        UPDATE endereco_sigh.municipios SET latitude=-10.70, longitude=-48.41 WHERE cod_ibge='1718204'; -- Porto Nacional
        """
    )


def downgrade():
    op.drop_table("cbos", schema="sigh")
    op.drop_column("municipios", "latitude", schema="endereco_sigh")
    op.drop_column("municipios", "longitude", schema="endereco_sigh")
