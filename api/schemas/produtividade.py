from pydantic import BaseModel
from typing import Optional


class ProdutividadeProfissional(BaseModel):
    """Modelo para dados de produtividade de cada profissional."""
    profissional_nome: str
    cns_profissional: Optional[str]
    cbo_descricao: Optional[str]
    total_atendimentos: int
    pacientes_unicos: int
    media_diaria_atendimentos: float
