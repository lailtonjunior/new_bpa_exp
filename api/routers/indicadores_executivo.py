from datetime import date
from typing import List, Optional

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.engine import Connection

from ..date_utils import last_n_months, resolve_or_default
from ..database_connector import get_db_connection
from ..schemas.kpi import AtendimentoPeriodo, KpiExecutivo
from ..security import verify_api_key

router = APIRouter(prefix="/api/indicadores/executivo", tags=["Dashboard Executivo"], dependencies=[Depends(verify_api_key)])


@router.get("/kpis_principais", response_model=KpiExecutivo)
async def get_kpis_principais(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    conn: Connection = Depends(get_db_connection),
):
    """
    KPIs consolidados para o periodo escolhido.
    """
    try:
        if not data_inicio or not data_fim:
            hoje = date.today()
            data_inicio = hoje.replace(day=1)
            proximo_mes = data_inicio + relativedelta(months=1)
            data_fim = proximo_mes - relativedelta(days=1)
        data_inicio, data_fim = resolve_or_default(data_inicio, data_fim, data_inicio, data_fim)

        query = text(
            """
            SELECT 
                COUNT(l.id_lancamento) as total_atendimentos,
                COUNT(DISTINCT fi.cod_paciente) as pacientes_unicos,
                COALESCE(SUM(COALESCE(l.quantidade, 1)), 0) as faturamento_estimado_bruto
            FROM sigh.lancamentos AS l
            JOIN sigh.contas AS c ON l.cod_conta = c.id_conta
            JOIN sigh.ficha_amb_int AS fi ON c.cod_fia = fi.id_fia
            WHERE l.data BETWEEN :data_inicio AND :data_fim AND c.ativo = 't' AND c.status_conta = 'A';
        """
        )
        result = conn.execute(query, {"data_inicio": data_inicio, "data_fim": data_fim}).fetchone()
        if result:
            dados = dict(result._mapping)
            return KpiExecutivo(
                total_atendimentos_mes=dados.get("total_atendimentos", 0),
                pacientes_unicos_mes=dados.get("pacientes_unicos", 0),
                faturamento_estimado_mes=f"R$ {float(dados.get('faturamento_estimado_bruto', 0)):.2f}",
            )
        return KpiExecutivo(total_atendimentos_mes=0, pacientes_unicos_mes=0, faturamento_estimado_mes="R$ 0,00")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor ao consultar o banco: {e}")


@router.get("/atendimentos_por_periodo", response_model=List[AtendimentoPeriodo])
async def get_atendimentos_periodo(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    conn: Connection = Depends(get_db_connection),
):
    """
    Serie historica de atendimentos para o periodo escolhido.
    """
    try:
        default_inicio, default_fim = last_n_months(12)
        data_inicio, data_fim = resolve_or_default(data_inicio, data_fim, default_inicio, default_fim)

        query = text(
            """
            SELECT 
                DATE_TRUNC('month', l.data)::DATE as periodo,
                COUNT(l.id_lancamento) as total_atendimentos,
                COUNT(DISTINCT fi.cod_paciente) as pacientes_unicos
            FROM sigh.lancamentos AS l
            JOIN sigh.contas AS c ON l.cod_conta = c.id_conta
            JOIN sigh.ficha_amb_int AS fi ON c.cod_fia = fi.id_fia
            WHERE l.data BETWEEN :data_inicio AND :data_fim
              AND c.ativo = 't' AND c.status_conta = 'A'
            GROUP BY 1
            ORDER BY periodo ASC;
        """
        )

        results = conn.execute(query, {"data_inicio": data_inicio, "data_fim": data_fim}).fetchall()

        dados_formatados = [
            AtendimentoPeriodo(
                periodo=row._mapping["periodo"].strftime("%Y-%m"),
                total_atendimentos=row._mapping["total_atendimentos"],
                pacientes_unicos=row._mapping["pacientes_unicos"],
            )
            for row in results
        ]
        return dados_formatados
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar serie historica: {e}")
