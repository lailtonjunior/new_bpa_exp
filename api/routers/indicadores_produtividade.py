from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection

from ..date_utils import last_full_month, resolve_or_default
from ..database_connector import get_db_connection
from ..schemas.produtividade import ProdutividadeProfissional
from ..security import verify_api_key

router = APIRouter(prefix="/api/indicadores/produtividade", tags=["Dashboard de Produtividade"], dependencies=[Depends(verify_api_key)])


@router.get("/ranking_profissionais", response_model=List[ProdutividadeProfissional])
async def get_ranking_profissionais(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limit: int = 200,
    offset: int = 0,
    conn: Connection = Depends(get_db_connection),
):
    try:
        default_inicio, default_fim = last_full_month()
        data_inicio, data_fim = resolve_or_default(data_inicio, data_fim, default_inicio, default_fim)

        num_dias = (data_fim - data_inicio).days + 1
        if num_dias <= 0:
            num_dias = 1

        if limit <= 0 or limit > 1000:
            raise ValueError("limit deve estar entre 1 e 1000")
        if offset < 0:
            raise ValueError("offset nao pode ser negativo")

        query = text(
            """
            SELECT 
                pr.nm_prestador as profissional_nome,
                pr.cns as cns_profissional,
                NULL as cbo_descricao,
                COUNT(l.id_lancamento) as total_atendimentos,
                COUNT(DISTINCT fi.cod_paciente) as pacientes_unicos,
                ROUND(COUNT(l.id_lancamento)::numeric / :num_dias, 2) as media_diaria_atendimentos
            FROM sigh.lancamentos AS l
            JOIN sigh.contas AS c ON l.cod_conta = c.id_conta
            JOIN sigh.ficha_amb_int AS fi ON c.cod_fia = fi.id_fia
            JOIN sigh.prestadores AS pr ON l.cod_prestador = pr.id_prestador
            WHERE l.data BETWEEN :data_inicio AND :data_fim
              AND c.ativo = 't'
              AND c.status_conta = 'A'
            GROUP BY 1, 2, 3
            ORDER BY total_atendimentos DESC
            LIMIT :limit OFFSET :offset;
        """
        )
        params = {"data_inicio": data_inicio, "data_fim": data_fim, "num_dias": num_dias, "limit": limit, "offset": offset}
        results = conn.execute(query, params).fetchall()
        return [ProdutividadeProfissional(**row._mapping) for row in results]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ranking de produtividade: {e}")
