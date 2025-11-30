from pydantic import BaseModel
from typing import Optional


class AtendimentoMunicipio(BaseModel):
    """Modelo para dados de atendimentos por municipio."""
    municipio_ibge: Optional[str]
    municipio_nome: str
    uf: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    total_pacientes: int
