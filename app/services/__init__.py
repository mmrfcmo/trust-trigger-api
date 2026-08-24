"""Identity Engine: User and Organisation service layer."""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User, Organisation, AuditLog, UserRole
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.schemas import (
    UserCreate, UserUpdate, UserResponse,
    OrganisationCreate, OrganisationUpdate, OrganisationResponse,
    AuditLogResponse,
)


# ─── Audit Log Helper (shared across modules) ───────────────────────────────

async def _log_audit(
    db: AsyncSession,
    user_id: uuid.UUID,
    organisation_id: uuid.UUID,
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """Create an audit log entry. Used by all modules."""
    log = AuditLog(
        user_id=user_id,
        organisation_id=organisation_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    await db.flush()
    return log


# ─── Auth ───────────────────────────────────────────────────────────────────

async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
    full_name: str,
    organisation_name: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Tuple[User, Organisation]:
    """Register a new user with a new organisation. First user becomes admin."""
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    slug = organisation_name.lower().replace(" ", "-").replace("_", "-")[:100]
    org = Organisation(name=organisation_name, slug=slug)
    db.add(org)
    await db.flush()

    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=UserRole.admin,
        organisation_id=org.id,
        is_verified=True,
    )
    db.add(user)
    await db.flush()

    await _log_audit(db, user.id, org.id, "user.register", "user", str(user.id), {"email": email})
    await _log_audit(db, user.id, org.id, "organisation.create", "organisation", str(org.id), {"name": organisation_name})

    return user, org


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return None
    user.last_login_at = datetime.now(timezone.utc)
    await db.flush()
    return user


async def login_user(
    db: AsyncSession,
    email: str,
    password: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> Tuple[Optional[User], Optional[str]]:
    user = await authenticate_user(db, email, password)
    if not user:
        return None, None
    token = create_access_token({"sub": str(user.id), "org_id": str(user.organisation_id), "role": user.role.value})
    await _log_audit(db, user.id, user.organisation_id, "user.login", "user", str(user.id), {}, ip_address, user_agent)
    return user, token


async def reset_password_request(db: AsyncSession, email: str) -> Optional[str]:
    result = await db.execute(select(User).where(User.email == email, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        return None
    token = create_access_token({"sub": str(user.id), "purpose": "password_reset"})
    # Override expiry for reset tokens (30 min)
    from jose import jwt as jose_jwt
    from datetime import timedelta
    token = jose_jwt.encode(
        {"sub": str(user.id), "purpose": "password_reset", "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
        "change-me-to-a-random-secret",
        algorithm="HS256",
    )
    return token


async def confirm_password_reset(db: AsyncSession, token: str, new_password: str) -> bool:
    payload = decode_access_token(token)
    if not payload or payload.get("purpose") != "password_reset":
        return False
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        return False
    user.password_hash = hash_password(new_password)
    await db.flush()
    await _log_audit(db, user.id, user.organisation_id, "user.password_reset", "user", str(user.id), {})
    return True


# ─── User CRUD ──────────────────────────────────────────────────────────────

async def create_user(db: AsyncSession, data: UserCreate, actor_id: uuid.UUID) -> User:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
        organisation_id=data.organisation_id,
    )
    db.add(user)
    await db.flush()
    await _log_audit(db, actor_id, data.organisation_id, "user.create", "user", str(user.id),
                     {"email": data.email, "role": data.role.value})
    return user


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_users_by_organisation(db: AsyncSession, org_id: uuid.UUID, skip: int = 0, limit: int = 50) -> Tuple[List[User], int]:
    query = select(User).where(User.organisation_id == org_id).offset(skip).limit(limit).order_by(User.created_at.desc())
    count_query = select(func.count()).select_from(User).where(User.organisation_id == org_id)
    result = await db.execute(query)
    total = await db.scalar(count_query)
    return list(result.scalars().all()), total or 0


async def update_user(db: AsyncSession, user_id: uuid.UUID, data: UserUpdate, actor_id: uuid.UUID) -> Optional[User]:
    user = await get_user(db, user_id)
    if not user:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    await db.flush()
    await _log_audit(db, actor_id, user.organisation_id, "user.update", "user", str(user.id), update_data)
    return user


async def delete_user(db: AsyncSession, user_id: uuid.UUID, actor_id: uuid.UUID) -> bool:
    user = await get_user(db, user_id)
    if not user:
        return False
    user.is_active = False
    await db.flush()
    await _log_audit(db, actor_id, user.organisation_id, "user.deactivate", "user", str(user.id), {})
    return True


# ─── Organisation CRUD ──────────────────────────────────────────────────────

async def create_organisation(db: AsyncSession, data: OrganisationCreate, actor_id: uuid.UUID) -> Organisation:
    org = Organisation(name=data.name, slug=data.slug, domain=data.domain)
    db.add(org)
    await db.flush()
    await _log_audit(db, actor_id, org.id, "organisation.create", "organisation", str(org.id), data.model_dump())
    return org


async def get_organisation(db: AsyncSession, org_id: uuid.UUID) -> Optional[Organisation]:
    result = await db.execute(select(Organisation).where(Organisation.id == org_id))
    return result.scalar_one_or_none()


async def update_organisation(db: AsyncSession, org_id: uuid.UUID, data: OrganisationUpdate, actor_id: uuid.UUID) -> Optional[Organisation]:
    org = await get_organisation(db, org_id)
    if not org:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(org, key, value)
    await db.flush()
    await _log_audit(db, actor_id, org_id, "organisation.update", "organisation", str(org_id), update_data)
    return org


# ─── Audit Log Queries ──────────────────────────────────────────────────────

async def get_audit_logs(
    db: AsyncSession,
    organisation_id: uuid.UUID,
    skip: int = 0,
    limit: int = 50,
    action: Optional[str] = None,
) -> Tuple[List[AuditLog], int]:
    query = select(AuditLog).where(AuditLog.organisation_id == organisation_id)
    count_query = select(func.count()).select_from(AuditLog).where(AuditLog.organisation_id == organisation_id)
    if action:
        query = query.where(AuditLog.action == action)
        count_query = count_query.where(AuditLog.action == action)
    query = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    total = await db.scalar(count_query)
    return list(result.scalars().all()), total or 0