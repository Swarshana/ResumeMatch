"""Application settings. Thresholds are calibration knobs, not universal facts."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent.parent
TAXONOMY_PATH = APP_DIR / "config" / "skill_taxonomy.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RTJ_",
        env_file=".env",
        extra="ignore",
    )

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    strong_threshold: float = Field(default=0.60, ge=0.0, le=1.0)
    partial_threshold: float = Field(default=0.30, ge=0.0, le=1.0)
    min_chunk_chars: int = Field(default=20, ge=1)
    max_chunk_chars: int = Field(default=420, ge=20)
    cors_origins: str = "*"

    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    if settings.partial_threshold >= settings.strong_threshold:
        raise ValueError("partial_threshold must be lower than strong_threshold")
    return settings
