from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.models.base import Base
from app.db.session import engine
from app.models.task import TaskORM
from app.models.category import CategoryORM
@asynccontextmanager
async def lifespan(_: FastAPI):
    from app.models.task import TaskORM
    from app.models.category import CategoryORM
    yield


settings = get_settings()
app = FastAPI(lifespan=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(api_router)