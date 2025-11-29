import logging
from fastapi import Header, HTTPException
from .config import get_api_key

logger = logging.getLogger(__name__)


async def verify_api_key(x_api_key: str = Header(default=None)):
    """
    Simple API key check using header X-API-Key.
    """
    expected = get_api_key()
    # Se nenhuma chave estiver configurada, nao valida (uso interno)
    if expected is None:
        return
    if not x_api_key or x_api_key != expected:
        logger.warning("Unauthorized access attempt with api key: %s", x_api_key)
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
