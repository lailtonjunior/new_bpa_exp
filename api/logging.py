import logging
import sys
import uuid
from contextvars import ContextVar
from time import perf_counter
from typing import Awaitable, Callable

from fastapi import Request, Response
from pythonjsonlogger import jsonlogger
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

# Contexto global para request_id e endpoint corrente
_request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
_endpoint_ctx: ContextVar[str | None] = ContextVar("endpoint", default=None)

# Métricas básicas de requisições HTTP
REQUEST_COUNTER = Counter(
    "api_requests_total",
    "Total de requisições HTTP por endpoint/método/status",
    ["endpoint", "method", "status"],
)


class ContextFilter(logging.Filter):
    """Inclui request_id e endpoint no registro mesmo quando não fornecidos via extra."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - simples
        record.request_id = _request_id_ctx.get() or "-"
        record.endpoint = _endpoint_ctx.get() or "-"
        return True


def setup_logging(level: int = logging.INFO) -> None:
    """Configura logging global em JSON com campos padronizados."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(module)s %(message)s %(request_id)s %(endpoint)s"
    )
    handler.setFormatter(formatter)
    handler.addFilter(ContextFilter())

    root = logging.getLogger()
    root.handlers = []
    root.setLevel(level)
    root.addHandler(handler)


def set_request_context(request_id: str | None, endpoint: str | None) -> None:
    _request_id_ctx.set(request_id)
    _endpoint_ctx.set(endpoint)


def clear_request_context() -> None:
    _request_id_ctx.set(None)
    _endpoint_ctx.set(None)


def get_request_id() -> str | None:
    return _request_id_ctx.get()


def build_request_id(header_value: str | None = None) -> str:
    return header_value or str(uuid.uuid4())


def create_request_id_middleware() -> Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]:
    async def middleware(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = build_request_id(request.headers.get("x-request-id"))
        endpoint = request.url.path
        set_request_context(request_id, endpoint)
        logger = logging.getLogger("api.request")
        started = perf_counter()
        logger.info(
            "request_start",
            extra={
                "event": "request_start",
                "method": request.method,
                "path": endpoint,
                "client": request.client.host if request.client else None,
            },
        )
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            REQUEST_COUNTER.labels(endpoint=endpoint, method=request.method, status=response.status_code).inc()
            duration_ms = round((perf_counter() - started) * 1000, 2)
            logger.info(
                "request_end",
                extra={
                    "event": "request_end",
                    "method": request.method,
                    "path": endpoint,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            return response
        except Exception:
            REQUEST_COUNTER.labels(endpoint=endpoint, method=request.method, status="500").inc()
            logger.exception("request_error", extra={"event": "request_error", "method": request.method, "path": endpoint})
            raise
        finally:
            clear_request_context()

    return middleware


def metrics_response() -> Response:
    """Retorna métricas do Prometheus."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def log_export_event(logger: logging.Logger, event: str, batch_size: int | None = None, status: str = "ok", **extra) -> None:
    payload = {"event": event, "status": status}
    if batch_size is not None:
        payload["batch_size"] = batch_size
    payload.update(extra)
    logger.info(event, extra=payload)
