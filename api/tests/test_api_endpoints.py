import sys
from pathlib import Path
import datetime

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.routers.indicadores_executivo import get_kpis_principais, get_atendimentos_periodo
from api.routers.indicadores_assistencial import (
    get_top_diagnosticos,
    get_perfil_etario,
    get_prevalencia_deficiencias,
)
from api.routers.indicadores_produtividade import get_ranking_profissionais
from api.routers.indicadores_territorial import get_atendimentos_por_municipio


class FakeResult:
    def __init__(self, rows=None):
        self.rows = rows or []

    def fetchone(self):
        return self.rows[0] if self.rows else None

    def fetchall(self):
        return self.rows


class FakeRow:
    def __init__(self, mapping):
        self._mapping = mapping


class FakeDate:
    def __init__(self, datestr):
        self._datestr = datestr

    def strftime(self, fmt):
        return self._datestr[:7]


class FakeConn:
    def __init__(self, mapping=None):
        self.mapping = mapping or {}
        self.calls = 0

    def execute(self, query, params=None):
        sql = str(query)
        self.calls += 1
        if "faltantes" in sql:
            return FakeResult([FakeRow({"faltantes": 0})])
        if "COUNT(l.id_lancamento)" in sql and "faturamento_total" in sql:
            return FakeResult(
                [FakeRow({"total_atendimentos": 5, "pacientes_unicos": 4, "faturamento_total": 250.50})]
            )
        if "DATE_TRUNC" in sql:
            return FakeResult(
                [
                    FakeRow({"periodo": FakeDate("2025-01-01"), "total_atendimentos": 2, "pacientes_unicos": 2}),
                    FakeRow({"periodo": FakeDate("2025-02-01"), "total_atendimentos": 3, "pacientes_unicos": 2}),
                ]
            )
        if "cid_codigo" in sql:
            return FakeResult([FakeRow({"cid_codigo": "A00", "cid_descricao": "Colera", "frequencia": 2})])
        if "faixa_etaria" in sql and "masculino" in sql:
            return FakeResult([FakeRow({"faixa_etaria": "0-4 anos", "masculino": 1, "feminino": 0})])
        if "paciente_diagnosticos" in sql:
            return FakeResult([FakeRow({"tipo": "Auditiva", "total_pacientes": 1})])
        if "media_diaria_atendimentos" in sql:
            return FakeResult(
                [
                    FakeRow(
                        {
                            "profissional_nome": "Dr. Teste",
                            "cns_profissional": "123",
                            "cbo_descricao": "Fisioterapeuta",
                            "total_atendimentos": 5,
                            "pacientes_unicos": 4,
                            "media_diaria_atendimentos": 2.5,
                        }
                    )
                ]
            )
        if "municipio_ibge" in sql:
            return FakeResult(
                [
                    FakeRow(
                        {
                            "municipio_ibge": "1721000",
                            "municipio_nome": "Palmas",
                            "uf": "TO",
                            "latitude": -10.18,
                            "longitude": -48.33,
                            "total_pacientes": 10,
                        }
                    )
                ]
            )
        return FakeResult([])


pytestmark = pytest.mark.anyio("asyncio")


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_executivo():
    conn = FakeConn()
    kpi = await get_kpis_principais(conn=conn, data_inicio=datetime.date(2025, 1, 1), data_fim=datetime.date(2025, 1, 31))
    assert kpi.total_atendimentos_mes == 5
    serie = await get_atendimentos_periodo(conn=conn, data_inicio=datetime.date(2024, 1, 1), data_fim=datetime.date(2025, 1, 1))
    assert len(serie) == 2


async def test_assistencial():
    conn = FakeConn()
    diag = await get_top_diagnosticos(conn=conn, data_inicio=datetime.date(2025, 1, 1), data_fim=datetime.date(2025, 1, 31))
    assert diag[0].cid_codigo == "A00"
    perfil = await get_perfil_etario(conn=conn, data_inicio=datetime.date(2025, 1, 1), data_fim=datetime.date(2025, 1, 31))
    assert perfil[0].masculino == 1
    preval = await get_prevalencia_deficiencias(conn=conn, data_inicio=datetime.date(2025, 1, 1), data_fim=datetime.date(2025, 1, 31))
    assert preval[0].tipo == "Auditiva"


async def test_produtividade():
    conn = FakeConn()
    prod = await get_ranking_profissionais(conn=conn, data_inicio=datetime.date(2025, 1, 1), data_fim=datetime.date(2025, 1, 31))
    assert prod[0].cbo_descricao == "Fisioterapeuta"


async def test_territorial():
    conn = FakeConn()
    terr = await get_atendimentos_por_municipio(conn=conn, data_inicio=datetime.date(2025, 1, 1), data_fim=datetime.date(2025, 1, 31))
    assert terr[0].latitude == -10.18
