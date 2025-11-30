import datetime
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.routers.indicadores_executivo import get_kpis_principais, format_currency_br


class FakeResult:
    def __init__(self, mapping):
        self._mapping = mapping

    def fetchone(self):
        return FakeResult(self._mapping)

    def fetchall(self):
        return [FakeResult(self._mapping)]


class FakeConn:
    def __init__(self, faturamento_total=0, faltantes=0):
        self.calls = 0
        self.faturamento_total = faturamento_total
        self.faltantes = faltantes

    def execute(self, query, params=None):
        # first call -> metrics, second call -> missing
        self.calls += 1
        if self.calls == 1:
            return FakeResult(
                {
                    "total_atendimentos": 10,
                    "pacientes_unicos": 8,
                    "faturamento_total": self.faturamento_total,
                }
            )
        return FakeResult({"faltantes": self.faltantes})


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio("asyncio")
async def test_get_kpis_principais_calculates_faturamento(monkeypatch):
    conn = FakeConn(faturamento_total=1234.56, faltantes=0)
    kpi = await get_kpis_principais(
        data_inicio=datetime.date(2025, 1, 1),
        data_fim=datetime.date(2025, 1, 31),
        conn=conn,
    )
    assert kpi.total_atendimentos_mes == 10
    assert kpi.pacientes_unicos_mes == 8
    assert kpi.faturamento_estimado_mes.startswith("R$ ")
    assert "1.234,56" in kpi.faturamento_estimado_mes


def test_format_currency_br():
    assert format_currency_br(1000) == "R$ 1.000,00"
    assert format_currency_br(0) == "R$ 0,00"
