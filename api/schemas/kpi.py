from pydantic import BaseModel


class KpiExecutivo(BaseModel):
    """Modelo para KPIs principais exibidos nos cards do Dashboard Executivo."""
    total_atendimentos_mes: int
    pacientes_unicos_mes: int
    faturamento_estimado_mes: str


class AtendimentoPeriodo(BaseModel):
    """Modelo para dados de atendimentos em um periodo (grafico de linhas)."""
    periodo: str
    total_atendimentos: int
    pacientes_unicos: int
