import logging
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.engine import Connection

from .config import get_allowed_origins
from .database_connector import get_db_connection
from .routers import indicadores_assistencial, indicadores_executivo, indicadores_produtividade, indicadores_territorial
from .security import verify_api_key

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Indicadores de Saude",
    description="Fornece dados para o dashboard de gestao da clinica.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(indicadores_executivo.router)
app.include_router(indicadores_assistencial.router)
app.include_router(indicadores_produtividade.router)
app.include_router(indicadores_territorial.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("REQUEST %s %s", request.method, request.url.path)
    response = await call_next(request)
    logger.info("RESPONSE %s %s -> %s", request.method, request.url.path, response.status_code)
    return response


@app.get("/", tags=["Health"])
def read_root():
    """Endpoint basico para verificar se a API esta no ar."""
    return {"status": "API de Indicadores de Saude - ativa"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.get("/ready", tags=["Health"])
def ready(conn: Connection = Depends(get_db_connection)):
    try:
        conn.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as exc:
        logger.exception("Readiness check failed")
        raise HTTPException(status_code=503, detail=f"Database not ready: {exc}")
