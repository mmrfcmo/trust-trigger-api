"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base, async_session_factory
from app.api.v1 import router as identity_router
from app.api.v1.lead_routes import router as lead_router
from app.api.v1.scan_routes import router as scan_router
from app.api.v1.score_routes import router as score_router
from app.api.v1.recommendation_routes import router as recommendation_router
from app.api.v1.proposal_routes import router as proposal_router
from app.api.v1.analytics_routes import router as analytics_router
from app.api.v1.prompt_routes import router as prompt_router
from app.api.v1.public_routes import router as public_router
from app.api.v1.report_viewer import router as report_router

# Import all models to ensure they are registered with Base.metadata
import app.models  # noqa
import app.models.trust_scan  # noqa
import app.models.scoring  # noqa
import app.models.recommendations  # noqa
import app.models.proposals  # noqa
import app.models.prompt_library  # noqa
import app.models.trust_framework  # noqa
import app.models.trust_journey  # noqa
import app.models.trust_standard_library  # noqa
import app.models.analytics  # noqa
import app.models.client_workspace  # noqa
import app.models.monitoring  # noqa
import app.models.publishing  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables and seed default data on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed default prompts and framework
    async with async_session_factory() as session:
        from app.services.seed_data import seed_default_prompts, seed_default_framework
        await seed_default_prompts(session)
        await seed_default_framework(session)
        from app.services.seed_standards import seed_standard_library
        await seed_standard_library(session)
        await session.commit()

    yield
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(identity_router)
app.include_router(lead_router)
app.include_router(scan_router)
app.include_router(score_router)
app.include_router(recommendation_router)
app.include_router(proposal_router)
app.include_router(analytics_router)
app.include_router(prompt_router)
app.include_router(public_router)
app.include_router(report_router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}

@app.get("/debug/env")
async def debug_env():
    """Debug endpoint to check env vars."""
    import os
    import sys
    return {
        "python_version": sys.version,
        "openai_key_set": bool(os.environ.get("OPENAI_API_KEY")),
        "openai_key_prefix": (os.environ.get("OPENAI_API_KEY", "")[:20] + "...") if os.environ.get("OPENAI_API_KEY") else "NOT SET",
        "cors": settings.cors_origins,
        "jwt_set": bool(os.environ.get("JWT_SECRET_KEY")),
    }
