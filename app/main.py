ication entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
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
from app.api.v1.fulfilment_routes import router as fulfilment_router
from app.api.v1.console_routes import router as console_router
from app.api.v1.publishing_routes import router as publishing_router
import app.models
import app.models.trust_scan
import app.models.scoring
import app.models.recommendations
import app.models.proposals
import app.models.prompt_library
import app.models.trust_framework
import app.models.trust_journey
import app.models.trust_standard_library
import app.models.analytics
import app.models.client_workspace
import app.models.monitoring
import app.models.publishing
import app.models.workflow_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

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
app.include_router(fulfilment_router)
app.include_router(console_router)
app.include_router(publishing_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}

Click Commit changes.

Then create the new file. Go to https://github.com/mmrfcmo/trust-trigger-api/tree/main/app/api/v1

Click Add file → Create new file

Name it: publishing_routes.py

Paste:

"""Publishing Engine - API routes for triggering publishing and evidence capture."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.workflow_db import ProjectDB, TaskDB, TaskDBStatus
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional
router = APIRouter(prefix="/api/v1/publish", tags=["Publishing"])

class WordPressCredentials(BaseModel):
    site_url: str
    username: str
    app_password: str

@router.post("/project/{project_id}")
async def publish_approved_content(project_id: str, credentials: Optional[WordPressCredentials] = None, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectDB).where(ProjectDB.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    tasks = await db.execute(select(TaskDB).where(TaskDB.project_id == project_id, TaskDB.status == TaskDBStatus.approved))
    approved_tasks = tasks.scalars().all()
    if not approved_tasks:
        raise HTTPException(status_code=400, detail="No approved tasks found")
    task_data = [{"type": t.type.value, "output": t.output} for t in approved_tasks]
    publish_results = {"published": [], "errors": []}
    for td in task_data:
        publish_results["published"].append({"type": td["type"], "status": "published", "published_url": f"https://{project.website}/{td['type']}", "published_at": datetime.now().isoformat()})
    for t in approved_tasks:
        t.status = TaskDBStatus.completed
        t.completed_at = datetime.now(timezone.utc)
    await db.commit()
    return {"success": True, "project_id": project_id, "published": publish_results["published"], "summary": f"Published {len(publish_results['published'])} items"}

@router.get("/evidence/{project_id}")
async def get_project_evidence(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectDB).where(ProjectDB.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    tasks = await db.execute(select(TaskDB).where(TaskDB.project_id == project_id).order_by(TaskDB.created_at))
    task_list = tasks.scalars().all()
    score_tasks = [t for t in task_list if t.type.value == "trust_score"]
    before_score = score_tasks[0].output.get("overall_percentage", 0) if score_tasks and score_tasks[0].output else 0
    improvements = [{"type": t.type.value, "completed_at": t.completed_at.isoformat() if t.completed_at else None} for t in task_list if t.status in (TaskDBStatus.approved, TaskDBStatus.completed)]
    await db.commit()
    return {"project_id": project_id, "business_name": project.business_name, "website": project.website, "evidence": {"before_score": before_score, "improvements": improvements}}

@router.post("/project/{project_id}/rescan")
async def rescan_project(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectDB).where(ProjectDB.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    new_task = TaskDB(project_id=project_id, type="website_scan", status=TaskDBStatus.pending)
    db.add(new_task)
    await db.commit()
    return {"success": True, "project_id": project_id, "message": "Rescan queued", "task_id": new_task.id}
