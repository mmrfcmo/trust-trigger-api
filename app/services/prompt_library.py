"""Prompt Library Service: CRUD for versioned prompt templates."""
import uuid
from typing import Optional, List, Tuple
from datetime import datetime, timezone
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.prompt_library import PromptTemplate, PromptVersionHistory, PromptCategory
from app.services import _log_audit


async def create_prompt(
    db: AsyncSession,
    category: PromptCategory,
    name: str,
    system_prompt: str,
    user_prompt_template: str,
    organisation_id: Optional[uuid.UUID] = None,
    created_by: Optional[uuid.UUID] = None,
    description: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    model: str = "gpt-4o-mini",
    variables: Optional[list] = None,
    tags: Optional[list] = None,
) -> PromptTemplate:
    """Create a new prompt template (version 1)."""
    prompt = PromptTemplate(
        organisation_id=organisation_id,
        category=category,
        name=name,
        description=description,
        version=1,
        is_active=True,
        system_prompt=system_prompt,
        user_prompt_template=user_prompt_template,
        temperature=temperature,
        max_tokens=max_tokens,
        model=model,
        variables=variables or [],
        tags=tags or [],
        created_by=created_by,
    )
    db.add(prompt)
    await db.flush()

    # Save version history
    await _save_version(db, prompt.id, 1, system_prompt, user_prompt_template,
                        temperature, max_tokens, model, "Initial version", created_by)

    if organisation_id and created_by:
        await _log_audit(db, created_by, organisation_id, "prompt.create", "prompt_template",
                         str(prompt.id), {"category": category.value, "name": name})

    return prompt


async def update_prompt(
    db: AsyncSession,
    prompt_id: uuid.UUID,
    organisation_id: Optional[uuid.UUID] = None,
    **kwargs,
) -> Optional[PromptTemplate]:
    """Update a prompt template. Auto-increments version and saves history."""
    query = select(PromptTemplate).where(PromptTemplate.id == prompt_id)
    if organisation_id:
        query = query.where(PromptTemplate.organisation_id == organisation_id)

    result = await db.execute(query)
    prompt = result.scalar_one_or_none()
    if not prompt:
        return None

    old_version = prompt.version
    new_version = old_version + 1

    update_data = {k: v for k, v in kwargs.items() if hasattr(prompt, k)}
    for key, value in update_data.items():
        setattr(prompt, key, value)
    prompt.version = new_version
    prompt.updated_at = datetime.now(timezone.utc)

    await db.flush()

    # Save version history
    await _save_version(
        db, prompt_id, new_version,
        kwargs.get("system_prompt", prompt.system_prompt),
        kwargs.get("user_prompt_template", prompt.user_prompt_template),
        kwargs.get("temperature", prompt.temperature),
        kwargs.get("max_tokens", prompt.max_tokens),
        kwargs.get("model", prompt.model),
        kwargs.get("change_notes", f"Updated from v{old_version}"),
        kwargs.get("changed_by"),
    )

    return prompt


async def _save_version(
    db: AsyncSession,
    prompt_id: uuid.UUID,
    version: int,
    system_prompt: str,
    user_prompt_template: str,
    temperature: float,
    max_tokens: int,
    model: str,
    change_notes: Optional[str] = None,
    changed_by: Optional[uuid.UUID] = None,
):
    history = PromptVersionHistory(
        prompt_id=prompt_id,
        version=version,
        system_prompt=system_prompt,
        user_prompt_template=user_prompt_template,
        temperature=temperature,
        max_tokens=max_tokens,
        model=model,
        change_notes=change_notes,
        changed_by=changed_by,
    )
    db.add(history)
    await db.flush()


async def get_active_prompt(
    db: AsyncSession,
    category: PromptCategory,
    organisation_id: Optional[uuid.UUID] = None,
) -> Optional[PromptTemplate]:
    """Get the active prompt template for a category (org-specific or global)."""
    query = select(PromptTemplate).where(
        PromptTemplate.category == category,
        PromptTemplate.is_active == True,
    )
    if organisation_id:
        query = query.where(PromptTemplate.organisation_id == organisation_id)
    else:
        query = query.where(PromptTemplate.organisation_id.is_(None))

    query = query.order_by(desc(PromptTemplate.version)).limit(1)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_prompts(
    db: AsyncSession,
    organisation_id: Optional[uuid.UUID] = None,
    category: Optional[PromptCategory] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[PromptTemplate], int]:
    """List prompt templates."""
    query = select(PromptTemplate)
    count_query = select(func.count()).select_from(PromptTemplate)

    if organisation_id:
        query = query.where(
            (PromptTemplate.organisation_id == organisation_id) |
            (PromptTemplate.organisation_id.is_(None))
        )
        count_query = count_query.where(
            (PromptTemplate.organisation_id == organisation_id) |
            (PromptTemplate.organisation_id.is_(None))
        )
    else:
        query = query.where(PromptTemplate.organisation_id.is_(None))
        count_query = count_query.where(PromptTemplate.organisation_id.is_(None))

    if category:
        query = query.where(PromptTemplate.category == category)
        count_query = count_query.where(PromptTemplate.category == category)

    query = query.order_by(desc(PromptTemplate.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    total = await db.scalar(count_query)
    return list(result.scalars().all()), total or 0


async def get_prompt_version_history(
    db: AsyncSession,
    prompt_id: uuid.UUID,
    limit: int = 20,
) -> List[PromptVersionHistory]:
    """Get version history for a prompt."""
    result = await db.execute(
        select(PromptVersionHistory)
        .where(PromptVersionHistory.prompt_id == prompt_id)
        .order_by(desc(PromptVersionHistory.version))
        .limit(limit)
    )
    return list(result.scalars().all())