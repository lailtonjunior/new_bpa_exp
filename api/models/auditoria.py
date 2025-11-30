import sqlalchemy as sa

from .base import Base, TimestampMixin


class AuditoriaExportacao(Base, TimestampMixin):
    __tablename__ = "auditoria_exportacao"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    tipo = sa.Column(sa.String(10), nullable=False, index=True)
    data_execucao = sa.Column(sa.DateTime(timezone=True), nullable=False)
    registros_processados = sa.Column(sa.Integer, nullable=False, default=0)
    erros = sa.Column(sa.Text, nullable=True)
    usuario = sa.Column(sa.String(120), nullable=True)
