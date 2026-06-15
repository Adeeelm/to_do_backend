import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str
    cors_origins: list[str]


def get_settings() -> Settings:
    database_url = os.environ["DATABASE_URL"]
    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    return Settings(database_url=database_url, cors_origins=cors_origins)
