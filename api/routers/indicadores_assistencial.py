from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection

from ..date_utils import last_n_days, last_n_months, resolve_or_default
from ..database_connector import get_db_connection
from ..schemas.assistencial import PerfilEtario, PrevalenciaDeficiencia, TopDiagnostico
from ..security import verify_api_key

router = APIRouter(prefix="/api/indicadores/assistencial", tags=["Dashboard Assistencial"], dependencies=[Depends(verify_api_key)])


@router.get("/top_diagnosticos", response_model=List[TopDiagnostico])
async def get_top_diagnosticos(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limit: int = 50,
    offset: int = 0,
    conn: Connection = Depends(get_db_connection),
):
    try:
        default_inicio, default_fim = last_n_days(90)
        data_inicio, data_fim = resolve_or_default(data_inicio, data_fim, default_inicio, default_fim)
        if limit <= 0 or limit > 500:
            raise ValueError("limit deve estar entre 1 e 500")
        if offset < 0:
            raise ValueError("offset nao pode ser negativo")

        query = text(
            """
            SELECT 
                l.cod_cid as cid_codigo,
                l.cod_cid as cid_descricao,
                COUNT(l.id_lancamento) as frequencia
            FROM sigh.lancamentos AS l
            JOIN sigh.contas AS c ON l.cod_conta = c.id_conta
            JOIN sigh.ficha_amb_int AS fi ON c.cod_fia = fi.id_fia
            WHERE l.data BETWEEN :data_inicio AND :data_fim
              AND l.cod_cid IS NOT NULL
              AND c.ativo = 't' AND c.status_conta = 'A'
            GROUP BY 1, 2
            ORDER BY frequencia DESC
            LIMIT :limit OFFSET :offset;
        """
        )
        results = conn.execute(query, {"data_inicio": data_inicio, "data_fim": data_fim, "limit": limit, "offset": offset}).fetchall()
        return [TopDiagnostico(**row._mapping) for row in results]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar top diagnosticos: {e}")


@router.get("/perfil_etario", response_model=List[PerfilEtario])
async def get_perfil_etario(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    conn: Connection = Depends(get_db_connection),
):
    try:
        default_inicio, default_fim = last_n_months(12)
        data_inicio, data_fim = resolve_or_default(data_inicio, data_fim, default_inicio, default_fim)

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
                CASE
                    WHEN age(p.data_nasc) BETWEEN '0 years' AND '4 years' THEN '0-4 anos'
                    WHEN age(p.data_nasc) BETWEEN '5 years' AND '9 years' THEN '5-9 anos'
                    WHEN age(p.data_nasc) BETWEEN '10 years' AND '14 years' THEN '10-14 anos'
                    WHEN age(p.data_nasc) BETWEEN '15 years' AND '19 years' THEN '15-19 anos'
                    WHEN age(p.data_nasc) BETWEEN '20 years' AND '29 years' THEN '20-29 anos'
                    WHEN age(p.data_nasc) BETWEEN '30 years' AND '39 years' THEN '30-39 anos'
                    WHEN age(p.data_nasc) BETWEEN '40 years' AND '49 years' THEN '40-49 anos'
                    WHEN age(p.data_nasc) BETWEEN '50 years' AND '59 years' THEN '50-59 anos'
                    ELSE '60+ anos'
                END as faixa_etaria,
                SUM(CASE WHEN p.cod_sexo = '1' THEN 1 ELSE 0 END) as masculino,
                SUM(CASE WHEN p.cod_sexo = '2' THEN 1 ELSE 0 END) as feminino
            FROM sigh.pacientes p
            JOIN pacientes_periodo pp ON p.id_paciente = pp.cod_paciente
            WHERE p.data_nasc IS NOT NULL
            GROUP BY faixa_etaria
            ORDER BY MIN(age(p.data_nasc));
        """
        )
        results = conn.execute(query, {"data_inicio": data_inicio, "data_fim": data_fim}).fetchall()
        return [PerfilEtario(**row._mapping) for row in results]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar perfil etario: {e}")


@router.get("/prevalencia_deficiencias", response_model=List[PrevalenciaDeficiencia])
async def get_prevalencia_deficiencias(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    conn: Connection = Depends(get_db_connection),
):
    try:
        default_inicio, default_fim = last_n_months(12)
        data_inicio, data_fim = resolve_or_default(data_inicio, data_fim, default_inicio, default_fim)

        query = text(
            """
            WITH paciente_diagnosticos AS (
                SELECT DISTINCT 
                    fi.cod_paciente,
                    CASE
                        WHEN l.cod_cid ILIKE 'F%' THEN 'Intelectual / Mental'
                        WHEN l.cod_cid ILIKE 'G%' THEN 'Fisica / Neurologica'
                        WHEN l.cod_cid BETWEEN 'H60' AND 'H95' THEN 'Auditiva'
                        WHEN l.cod_cid BETWEEN 'H00' AND 'H59' THEN 'Visual'
                        ELSE 'Outros'
                    END as tipo
                FROM sigh.lancamentos l
                JOIN sigh.contas c ON l.cod_conta = c.id_conta
                JOIN sigh.ficha_amb_int fi ON c.cod_fia = fi.id_fia
                WHERE l.data BETWEEN :data_inicio AND :data_fim
                  AND l.cod_cid IS NOT NULL AND l.cod_cid <> ''
            )
            SELECT 
                tipo,
                COUNT(cod_paciente) as total_pacientes
            FROM paciente_diagnosticos
            WHERE tipo <> 'Outros'
            GROUP BY tipo
            ORDER BY total_pacientes DESC;
        """
        )
        results = conn.execute(query, {"data_inicio": data_inicio, "data_fim": data_fim}).fetchall()
        return [PrevalenciaDeficiencia(**row._mapping) for row in results]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar prevalencia de deficiencias: {e}")
