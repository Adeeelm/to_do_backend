from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import logging
from time import perf_counter
from app.api.router import api_router
from app.core.config import get_settings
from app.models.base import Base
from app.db.session import engine
from app.models.task import TaskORM
from app.models.category import CategoryORM
from app.core.logging import configure_logging
@asynccontextmanager
async def lifespan(_: FastAPI):
    from app.models.task import TaskORM
    from app.models.category import CategoryORM
    yield


configure_logging()

settings = get_settings()
app = FastAPI()
logger = logging.getLogger("app.middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    started_at = perf_counter()
    try:
        response: Response = await call_next(request)  # Работа самого эндпоинта
    except Exception:
        duration_ms = (perf_counter() - started_at) * 1000
        logger.exception(
            "Request failed: %s %s completed_in=%.2fms",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (perf_counter() - started_at) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


_request_counter = 0
@app.middleware("http")
async def count_requests(request: Request, call_next) -> Response:
    global _request_counter
    _request_counter += 1
    request_number = _request_counter

    response: Response = await call_next(request)
    response.headers["X-Request-Number"] = str(request_number)
    return response
app.include_router(api_router)