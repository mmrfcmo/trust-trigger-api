"""Prompt Library API routes."""
import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user, require_role
from app.models import User, UserRole
from app.models.prompt_library import PromptCategory
from app.services.prompt_library import (
    create_prompt, update_prompt, get_active_prompt,
    get_prompts, get_prompt_version_history,
)
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/prompts", tags=["Prompt Library"])


class PromptCreate(BaseModel):
    category: PromptCategory
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    system_prompt: str = Field(..., min_length=10)
    user_prompt_template: str = Field(..., min_length=10)
    temperature: float = 0.7
    max_tokens: int = 2000
    model: str = "gpt-4o-mini"
    variables: Optional[list] = None
    tags: Optional[list] = None


class PromptUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt_template: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    model: Optional[str] = None
    variables: Optional[list] = None
    tags: Optional[list] = None
    is_active: Optional[bool] = None
    change_notes: Optional[str] = None


class PromptResponse(BaseModel):
    id: uuid.UUID
    organisation_id: Optional[uuid.UUID]
    category: PromptCategory
    name: str
    description: Optional[str]
    version: int
    is_active: bool
    system_prompt: str
    user_prompt_template: str
    temperature: float
    max_tokens: int
    model: str
    variables: list
    tags: list
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PromptList(BaseModel):
    items: list[PromptResponse]
    total: int
    page: int
    page_size: int


class VersionHistoryResponse(BaseModel):
    id: uuid.UUID
    prompt_id: uuid.UUID
    version: int
    system_prompt: str
    user_prompt_template: str
    temperature: float
    max_tokens: int
    model: str
    change_notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt_route(
    data: PromptCreate,
    current_user: User = Depends(require_role([UserRole.admin, UserRole.manager])),
    db: AsyncSession = Depends(get_db),
):
    """Create a new prompt template."""
    prompt = await create_prompt(
        db, data.category, data.name, data.system_prompt, data.user_prompt_template,
        organisation_id=current_user.organisation_id,
        created_by=current_user.id,
        description=data.description,
        temperature=data.temperature,
        max_tokens=data.max_tokens,
        model=data.model,
        variables=data.variables,
        tags=data.tags,
    )
    return PromptResponse.model_validate(prompt)


@router.get("", response_model=PromptList)
async def list_prompts(
    category: Optional[PromptCategory] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List prompt templates."""
    prompts, total = await get_prompts(db, current_user.organisation_id, category, skip, limit)
    return PromptList(
        items=[PromptResponse.model_validate(p) for p in prompts],
        total=total,
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get("/active/{category}", response_model=PromptResponse)
async def get_active_prompt_route(
    category: PromptCategory,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the active prompt for a category (org-specific or global fallback)."""
    prompt = await get_active_prompt(db, category, current_user.organisation_id)
    if not prompt:
        prompt = await get_active_prompt(db, category, None)
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active prompt found")
    return PromptResponse.model_validate(prompt)


@router.patch("/{prompt_id}", response_model=PromptResponse)
async def update_prompt_route(
    prompt_id: uuid.UUID,
    data: PromptUpdate,
    current_user: User = Depends(require_role([UserRole.admin, UserRole.manager])),
    db: AsyncSession = Depends(get_db),
):
    """Update a prompt template (creates new version)."""
    prompt = await update_prompt(
        db, prompt_id, current_user.organisation_id,
        changed_by=current_user.id,
        **data.model_dump(exclude_unset=True),
    )
    if not prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return PromptResponse.model_validate(prompt)


@router.get("/{prompt_id}/versions", response_model=list[VersionHistoryResponse])
async def get_prompt_versions(
    prompt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get version history for a prompt."""
    history = await get_prompt_version_history(db, prompt_id)
    return [VersionHistoryResponse.model_validate(h) for h in history]