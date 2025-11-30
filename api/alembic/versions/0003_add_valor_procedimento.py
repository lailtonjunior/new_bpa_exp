"""Add valor_procedimento to procedimentos"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_add_valor_procedimento"
down_revision = "0002_create_core_schema"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "procedimentos",
        sa.Column("valor_procedimento", sa.Numeric(12, 2), nullable=False, server_default="0"),
        schema="sigh",
    )
    # exemplo de seed de valores (ajuste conforme tabela real)
    op.execute("UPDATE sigh.procedimentos SET valor_procedimento = 100.00 WHERE codigo_procedimento = '0301010048'")
    op.execute("UPDATE sigh.procedimentos SET valor_procedimento = 200.00 WHERE codigo_procedimento = '0301070075'")


def downgrade():
    op.drop_column("procedimentos", "valor_procedimento", schema="sigh")
