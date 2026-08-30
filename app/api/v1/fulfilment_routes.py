"""Fulfilment Dashboard - API routes for managing projects and tasks."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.workflow_db import ProjectDB, TaskDB, ProjectDBStatus, TaskDBStatus
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
router = APIRouter(prefix="/api/v1/fulfilment", tags=["Fulfilment"])

class ProjectSummary(BaseModel):
    id: str
    business_name: str
    website: str
    status: str
    product_type: str
    price: float
    progress: float = 0.0
    task_count: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_awaiting_review: int = 0
    created_at: datetime
    completed_at: Optional[datetime] = None
    class Config: from_attributes = True

class TaskSummary(BaseModel):
    id: str
    project_id: str
    type: str
    status: str
    depends_on: list[str] = []
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3
    output: dict = {}
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None
    class Config: from_attributes = True

class WorkflowDetail(BaseModel):
    project: ProjectSummary
    tasks: list[TaskSummary]

@router.get("/projects", response_model=list[ProjectSummary])
async def list_projects(status_filter: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    query = select(ProjectDB)
    if status_filter:
        query = query.where(ProjectDB.status == status_filter)
    query = query.order_by(ProjectDB.created_at.desc())
    result = await db.execute(query)
    projects = result.scalars().all()
    output = []
    for p in projects:
        tasks = await db.execute(select(TaskDB).where(TaskDB.project_id == p.id))
        task_list = tasks.scalars().all()
        total = len(task_list)
        completed = sum(1 for t in task_list if t.status in (TaskDBStatus.completed, TaskDBStatus.approved, TaskDBStatus.skipped))
        failed = sum(1 for t in task_list if t.status == TaskDBStatus.failed)
        awaiting = sum(1 for t in task_list if t.status == TaskDBStatus.awaiting_review)
        output.append(ProjectSummary(
            id=p.id, business_name=p.business_name, website=p.website,
            status=p.status.value, product_type=p.product_type, price=p.price,
            progress=completed / total if total > 0 else 0.0,
            task_count=total, tasks_completed=completed, tasks_failed=failed,
            tasks_awaiting_review=awaiting, created_at=p.created_at, completed_at=p.completed_at,
        ))
    return output

@router.get("/projects/{project_id}", response_model=WorkflowDetail)
async def get_project_workflow(project_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectDB).where(ProjectDB.id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    tasks_result = await db.execute(select(TaskDB).where(TaskDB.project_id == project_id).order_by(TaskDB.created_at))
    tasks = tasks_result.scalars().all()
    task_summaries = []
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status in (TaskDBStatus.completed, TaskDBStatus.approved, TaskDBStatus.skipped))
    for t in tasks:
        task_summaries.append(TaskSummary(
            id=t.id, project_id=t.project_id, type=t.type.value, status=t.status.value,
            depends_on=t.depends_on, created_at=t.created_at, started_at=t.started_at,
            completed_at=t.completed_at, duration_seconds=t.duration_seconds,
            retry_count=t.retry_count, max_retries=t.max_retries, output=t.output,
            reviewed_by=t.reviewed_by, review_notes=t.review_notes,
        ))
    return WorkflowDetail(
        project=ProjectSummary(id=project.id, business_name=project.business_name, website=project.website,
            status=project.status.value, product_type=project.product_type, price=project.price,
            progress=completed / total if total > 0 else 0.0, task_count=total,
            tasks_completed=completed, tasks_failed=sum(1 for t in tasks if t.status == TaskDBStatus.failed),
            tasks_awaiting_review=sum(1 for t in tasks if t.status == TaskDBStatus.awaiting_review),
            created_at=project.created_at, completed_at=project.completed_at),
        tasks=task_summaries)

class ApprovalRequest(BaseModel):
    task_id: str
    approved: bool
    notes: str = ""

@router.post("/tasks/approve", status_code=status.HTTP_200_OK)
async def approve_or_reject_task(req: ApprovalRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaskDB).where(TaskDB.id == req.task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = TaskDBStatus.approved if req.approved else TaskDBStatus.rejected
    task.reviewed_at = datetime.now(timezone.utc)
    task.review_notes = req.notes
    await db.commit()
    return {"success": True, "task_id": req.task_id, "new_status": task.status.value}

@router.post("/tasks/{task_id}/regenerate")
async def regenerate_task(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaskDB).where(TaskDB.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = TaskDBStatus.pending
    task.retry_count = 0
    task.output = {}
    task.reviewed_by = None
    task.reviewed_at = None
    await db.commit()
    return {"success": True, "task_id": task_id, "new_status": task.status.value}

@router.post("/projects/from-lead/{lead_id}", status_code=status.HTTP_201_CREATED)
async def create_project_from_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    from app.models import Lead
    lead_result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = lead_result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    project = ProjectDB(
        organisation_id=lead.organisation_id, lead_id=lead.id,
        business_name=lead.business_name, website=lead.website or "", email=lead.email or "",
        status=ProjectDBStatus.active)
    db.add(project)
    await db.flush()
    for td in [{"type": "website_scan", "depends_on": []},
               {"type": "google_business_scan", "depends_on": []},
               {"type": "trust_score", "depends_on": ["website_scan", "google_business_scan"]},
               {"type": "evidence_capture", "depends_on": ["website_scan"]},
               {"type": "homepage_copy", "depends_on": ["trust_score"], "status": "awaiting_review"},
               {"type": "email_sequence", "depends_on": ["trust_score"], "status": "awaiting_review"},
               {"type": "google_business_posts", "depends_on": ["trust_score"], "status": "awaiting_review"},
               {"type": "social_media_posts", "depends_on": ["trust_score"], "status": "awaiting_review"},
               {"type": "trust_snapshot_report", "depends_on": ["trust_score"]}]:
        t = TaskDB(project_id=project.id, type=td["type"], depends_on=td["depends_on"], status=td.get("status", "pending"))
        db.add(t)
    await db.commit()
    return {"success": True, "project_id": project.id, "lead_id": lead_id, "tasks_created": 9}
