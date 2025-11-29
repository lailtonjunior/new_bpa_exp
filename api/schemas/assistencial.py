from pydantic import BaseModel


class TopDiagnostico(BaseModel):
    """Modelo para dados de um diagnostico no ranking."""
    cid_codigo: str
    cid_descricao: str
    frequencia: int


class PerfilEtario(BaseModel):
    """Modelo para dados da piramide etaria."""
    faixa_etaria: str
    masculino: int
    feminino: int


class PrevalenciaDeficiencia(BaseModel):
    """Modelo para dados de prevalencia de deficiencias."""
    tipo: str
    total_pacientes: int
