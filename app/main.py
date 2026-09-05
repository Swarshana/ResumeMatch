from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config.settings import get_settings
from app.services.analyzer import get_embedder


@asynccontextmanager
async def lifespan(application: FastAPI):
    if getattr(application.state, "warmup_embedder", True):
        get_embedder()
    yield


def create_app(*, warmup_embedder: bool = True) -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="Resume-to-Job-Match Analyzer",
        description="Semantic resume-to-job alignment with skill-cluster gap analysis.",
        version="0.1.0",
        lifespan=lifespan,
    )
    application.state.warmup_embedder = warmup_embedder
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list(),
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(router, prefix="/api")

    @application.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()
