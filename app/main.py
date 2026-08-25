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


@app.get("/debug/test-openai")
async def debug_test_openai():
    """Test if openai can be imported and called."""
    import os
    result = {"steps": {}}
    
    try:
        import openai
        result["steps"]["import"] = f"ok (version={openai.__version__})"
    except Exception as e:
        result["steps"]["import"] = f"FAILED: {str(e)}"
        return result
    
    key = os.environ.get("OPENAI_API_KEY", "")
    result["steps"]["key_raw"] = {
        "length": len(key),
        "first_10": key[:10],
        "last_10": key[-10:] if len(key) > 10 else "",
        "contains_ellipsis": "\u2026" in key,
        "is_sk_proj": key.startswith("sk-proj"),
        "is_sk_pro": key.startswith("sk-pro"),
    }
    
    result["steps"]["key_check"] = f"ok (length={len(key)}, prefix={key[:20]}...)"
    
    try:
        import httpx
        result["steps"]["httpx"] = "ok"
    except Exception as e:
        result["steps"]["httpx"] = f"FAILED: {str(e)}"
    
    return result
    
    # Step 2: Check API key
    try:
        key = os.environ.get("OPENAI_API_KEY", "")
        result["steps"]["key_check"] = f"ok (length={len(key)}, prefix={key[:20]}...)"
    except Exception as e:
        result["steps"]["key_check"] = f"FAILED: {str(e)}"
    
    # Step 3: Try a simple API call
    try:
        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        result["steps"]["api_call_attempt"] = "attempting..."
        # Just check if we can list models (lightweight test)
        import httpx
        result["steps"]["httpx"] = "ok"
    except Exception as e:
        result["steps"]["api_call_attempt"] = f"FAILED: {str(e)}"
        result["traceback"] = traceback.format_exc()
    
    return result


@app.get("/debug/check-models")
async def debug_check_models():
    """Check if all pydantic models can be imported and validated."""
    import traceback
    import sys
    result = {}
    
    # Check all schema models
    models_to_check = [
        ("app.schemas", "all"),
        ("app.schemas.scoring", "TrustScoreResponse, TrustScoreList, ScoreHistoryPoint, PillarScore, ImprovementAction"),
        ("app.schemas.recommendations", "RecommendationResponse, RecommendationList, GenerateRecommendationRequest"),
        ("app.schemas.trust_scan", "ScanResponse, ScanList"),
        ("app.api.v1.public_routes", "TrustSnapshotRequest, TrustSnapshotResponse"),
        ("app.api.v1.analytics_routes", "DashboardResponse"),
        ("app.api.v1.proposal_routes", "ProposalResponse, ProposalList"),
        ("app.api.v1.prompt_routes", "PromptResponse, PromptList, VersionHistoryResponse"),
    ]
    
    for module_path, classes in models_to_check:
        try:
            __import__(module_path)
            module = sys.modules[module_path]
            result[module_path] = "imported OK"
        except Exception as e:
            result[module_path] = f"IMPORT FAILED: {str(e)}"
            result[f"{module_path}_traceback"] = traceback.format_exc()
    
    return result
