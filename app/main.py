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

@app.get("/debug/test-ai")
async def debug_test_ai():
    """Test if OpenAI API call works."""
    import os
    result = {"steps": {}}
    
    try:
        import openai
        result["openai_version"] = openai.__version__
    except Exception as e:
        result["openai_import_error"] = str(e)
        return result
    
    try:
        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        result["key_length"] = len(openai.api_key)
        
        # Try a simple completion
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello in one word"}],
            max_tokens=10,
        )
        result["api_call"] = "ok"
        result["response"] = response.choices[0].message.content
        result["model_used"] = response.model
    except Exception as e:
        result["api_call_error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()[-500:]
    
    return result


@app.get("/debug/test-flow")
async def debug_test_flow(db: AsyncSession = Depends(get_db)):
    """Test the Trust Snapshot flow step by step."""
    import traceback
    from fastapi.responses import JSONResponse
    from app.models import Lead, Organisation, User, UserRole
    from app.models.trust_scan import TrustScan, ScanType, ScanStatus
    from app.models.scoring import TrustScoreRecord, TrustGrade
    from app.models.recommendations import AIRecommendation, RecommendationType
    from app.models.trust_journey import TrustJourney, JourneyMilestone
    from app.core.security import hash_password
    from app.services.lead_intelligence import calculate_opportunity_score
    from app.services.trust_scanner import run_scan
    from app.services.scoring import compute_trust_score, build_score_response
    from app.services.recommendations import generate_recommendation
    from sqlalchemy import select, text
    
    results = {}
    
    # Step 1: DB connection
    try:
        await db.execute(text("SELECT 1"))
        results["db"] = "ok"
    except Exception as e:
        results["db"] = f"FAILED: {str(e)}"
        return JSONResponse(results)
    
    # Step 2: Get or create org
    try:
        r = await db.execute(select(Organisation).where(Organisation.slug == "debug-test"))
        org = r.scalar_one_or_none()
        if not org:
            org = Organisation(name="Debug Test", slug="debug-test", settings={"test": True})
            db.add(org)
            await db.flush()
        results["org"] = f"ok (id={org.id})"
    except Exception as e:
        results["org"] = f"FAILED: {str(e)}"
        await db.rollback()
        return JSONResponse(results)
    
    # Step 3: Create user
    try:
        r = await db.execute(select(User).where(User.email == "debug@test.com"))
        user = r.scalar_one_or_none()
        if not user:
            user = User(email="debug@test.com", password_hash=hash_password("test1234"), full_name="Debug", role=UserRole.admin, organisation_id=org.id, is_active=True, is_verified=True)
            db.add(user)
            await db.flush()
        results["user"] = f"ok (id={user.id})"
    except Exception as e:
        results["user"] = f"FAILED: {str(e)}"
        await db.rollback()
        return JSONResponse(results)
    
    # Step 4: Create lead
    try:
        lead = Lead(organisation_id=org.id, business_name="Debug Business", website="https://example.com", email="debug@example.com", source="manual", opportunity_score=50, opportunity_reason="Test")
        db.add(lead)
        await db.flush()
        results["lead"] = f"ok (id={lead.id})"
    except Exception as e:
        results["lead"] = f"FAILED: {str(e)}"
        await db.rollback()
        return JSONResponse(results)
    
    # Step 5: Run scan
    try:
        scan = await run_scan(db, lead.id, org.id, user.id, ScanType.full)
        results["scan"] = f"ok (id={scan.id}, status={scan.status})"
    except Exception as e:
        results["scan"] = f"FAILED: {str(e)}"
        results["scan_traceback"] = traceback.format_exc()[-300:]
        await db.rollback()
        return JSONResponse(results)
    
    # Step 6: Compute score
    try:
        if scan and scan.status == ScanStatus.completed:
            record = await compute_trust_score(db, scan.id, org.id, lead.id, user.id)
            score = build_score_response(record)
            results["score"] = f"ok (id={record.id}, score={score.overall_percentage}%)"
        else:
            results["score"] = f"skipped (scan status: {scan.status if scan else 'None'})"
    except Exception as e:
        results["score"] = f"FAILED: {str(e)}"
        results["score_traceback"] = traceback.format_exc()[-300:]
        await db.rollback()
        return JSONResponse(results)
    
    # Step 7: Generate report
    try:
        rec = await generate_recommendation(db, lead.id, RecommendationType.trust_snapshot, org.id, user.id)
        results["report"] = f"ok (id={rec.id})"
    except Exception as e:
        results["report"] = f"FAILED: {str(e)}"
        results["report_traceback"] = traceback.format_exc()[-500:]
    
    await db.rollback()
    return JSONResponse(results)
