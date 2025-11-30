import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from api.async_db import get_async_session
from api.main import app
from api.models import Base
from api.security import verify_api_key


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch):
    monkeypatch.setenv("APP_API_KEY", "test-key")


@pytest.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_session():
        async with Session() as session:
            yield session

    app.dependency_overrides[get_async_session] = override_session
    app.dependency_overrides[verify_api_key] = lambda: None

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides = {}
    await engine.dispose()


@pytest.mark.anyio
async def test_criar_e_listar_auditorias(client: AsyncClient):
    payload = {
        "tipo": "BPA",
        "data_execucao": datetime.datetime.utcnow().isoformat(),
        "registros_processados": 10,
        "erros": "nenhum",
        "usuario": "tester",
    }
    resp = await client.post("/api/auditorias", json=payload)
    assert resp.status_code == 201
    created = resp.json()
    assert created["id"] > 0
    assert created["tipo"] == "BPA"

    resp_list = await client.get("/api/auditorias?limit=5&offset=0")
    assert resp_list.status_code == 200
    body = resp_list.json()
    assert body["total"] == 1
    assert body["items"][0]["usuario"] == "tester"
