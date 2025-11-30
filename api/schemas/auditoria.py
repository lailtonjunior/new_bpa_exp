import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class TipoAuditoria(str, Enum):
    BPA = "BPA"
    APAC = "APAC"
    CIHA = "CIHA"


class AuditoriaBase(BaseModel):
    tipo: TipoAuditoria
    data_execucao: datetime.datetime = Field(..., description="Data e hora da execucao")
    registros_processados: int = Field(ge=0)
    erros: Optional[str] = None
    usuario: Optional[str] = None


class AuditoriaCreate(AuditoriaBase):
    pass


class AuditoriaRead(AuditoriaBase):
    id: int
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    class Config:
        orm_mode = True


class AuditoriaList(BaseModel):
    items: List[AuditoriaRead]
    total: int
    limit: int
    offset: int
