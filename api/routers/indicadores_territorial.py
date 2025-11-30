from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection

from ..date_utils import last_n_months, resolve_or_default
from ..database_connector import get_db_connection
from ..schemas.territorial import AtendimentoMunicipio
from ..security import verify_api_key

router = APIRouter(prefix="/api/indicadores/territorial", tags=["Dashboard Territorial"], dependencies=[Depends(verify_api_key)])


@router.get("/atendimentos_por_municipio", response_model=List[AtendimentoMunicipio])
async def get_atendimentos_por_municipio(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limit: int = 200,
    offset: int = 0,
    conn: Connection = Depends(get_db_connection),
):
    try:
        default_inicio, default_fim = last_n_months(12)
        data_inicio, data_fim = resolve_or_default(data_inicio, data_fim, default_inicio, default_fim)
        if limit <= 0 or limit > 1000:
            raise ValueError("limit deve estar entre 1 e 1000")
        if offset < 0:
            raise ValueError("offset nao pode ser negativo")

        query = text(
            """
            WITH pacientes_periodo AS (
                SELECT DISTINCT fi.cod_paciente
                FROM sigh.lancamentos l
                JOIN sigh.contas c ON l.cod_conta = c.id_conta
                JOIN sigh.ficha_amb_int fi ON c.cod_fia = fi.id_fia
                WHERE l.data BETWEEN :data_inicio AND :data_fim
            )
            SELECT
                m.cod_ibge as municipio_ibge,
                m.nome as municipio_nome,
                m.uf,
                m.latitude,
                m.longitude,
                COUNT(DISTINCT p.id_paciente) as total_pacientes
            FROM sigh.pacientes p
            JOIN pacientes_periodo pp ON p.id_paciente = pp.cod_paciente
            JOIN sigh.enderecos e ON p.id_paciente = e.cod_paciente
            JOIN endereco_sigh.logradouros lg ON e.cod_logradouro = lg.id_logradouro
            JOIN endereco_sigh.municipios m ON lg.cod_municipio = m.id_municipio
            WHERE e.ativo = 't'
            GROUP BY 1, 2, 3
            ORDER BY total_pacientes DESC
            LIMIT :limit OFFSET :offset;
        """
        )
        params = {"data_inicio": data_inicio, "data_fim": data_fim, "limit": limit, "offset": offset}
        results = conn.execute(query, params).fetchall()
        return [AtendimentoMunicipio(**row._mapping) for row in results]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar dados territoriais: {e}")
