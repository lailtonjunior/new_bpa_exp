from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..async_db import get_async_session
from ..models import AuditoriaExportacao
from ..schemas.auditoria import AuditoriaCreate, AuditoriaList, AuditoriaRead
from ..security import verify_api_key

router = APIRouter(
    prefix="/api/auditorias",
    tags=["Auditoria Exportacao"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("", response_model=AuditoriaRead, status_code=status.HTTP_201_CREATED)
async def registrar_auditoria(
    payload: AuditoriaCreate, session: AsyncSession = Depends(get_async_session)
) -> AuditoriaRead:
    auditoria = AuditoriaExportacao(**payload.model_dump())
    session.add(auditoria)
    await session.commit()
    await session.refresh(auditoria)
    return auditoria


@router.get("", response_model=AuditoriaList)
async def listar_auditorias(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tipo: Optional[str] = Query(None, description="Filtra por tipo (BPA, APAC, CIHA)"),
    session: AsyncSession = Depends(get_async_session),
) -> AuditoriaList:
    query = select(AuditoriaExportacao)
    if tipo:
        query = query.where(AuditoriaExportacao.tipo == tipo)

    total_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(total_query)
    total = total_result.scalar_one()

    result = await session.execute(
        query.order_by(AuditoriaExportacao.data_execucao.desc(), AuditoriaExportacao.id.desc())
        .offset(offset)
        .limit(limit)
    )
    items = result.scalars().all()
    return AuditoriaList(items=items, total=total, limit=limit, offset=offset)
