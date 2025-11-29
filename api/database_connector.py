import logging
from fastapi import HTTPException

from shared.database import Database
from .config import get_db_settings

logger = logging.getLogger(__name__)


def get_db_connection():
    """
    FastAPI dependency that opens and closes one database connection per request.
    Prefers environment variables (APP_DB_*) and falls back to config.ini.
    """
    db = Database()
    try:
        settings = get_db_settings()
    except RuntimeError as exc:
        logger.error("Database settings missing: %s", exc)
        raise HTTPException(status_code=500, detail="Database configuration is missing")

    sucesso, mensagem = db.conectar(
        db_name=settings["db_name"],
        user=settings["db_user"],
        password=settings["db_password"],
        host=settings["db_host"],
        port=settings["db_port"],
    )
    if not sucesso:
        raise HTTPException(status_code=503, detail=f"Falha ao conectar ao banco de dados: {mensagem}")

    try:
        yield db.conn
    finally:
        if db.conn:
            db.conn.close()
