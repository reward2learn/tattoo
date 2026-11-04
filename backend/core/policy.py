"""Central authorization: authenticated -> studio membership -> role -> resource ownership."""
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request

from core.db import db
from core.security import decode_token
from services.studios import Studio, get_studio_by_slug
from services.users import User, get_user


def _token(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    if not token:
        header = request.headers.get("Authorization", "")
        if header.startswith("Bearer "):
            token = header[7:]
    return token


async def get_current_user(request: Request) -> User:
    token = _token(request)
    if not token:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
    if payload.get("type") != "access":
        raise HTTPException(401, "Invalid token type")
    user = await get_user(payload.get("sub", ""))
    if not user or user.session_version != payload.get("sv"):
        raise HTTPException(401, "Session ended")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_platform_admin(user: CurrentUser) -> User:
    if not user.is_platform_admin:
        raise HTTPException(403, "You don't have access to this page")
    return user


PlatformAdmin = Annotated[User, Depends(require_platform_admin)]


def require_account_type(*types: str):
    async def dep(user: CurrentUser) -> User:
        if user.account_type not in types and not user.is_platform_admin:
            raise HTTPException(403, "Your account type cannot do this")
        return user
    return dep


@dataclass
class StudioContext:
    studio: Studio
    user: User
    role: str
    membership_id: str


def studio_role(*roles: str):
    """Active studio comes ONLY from the URL slug + the caller's active membership."""
    async def dep(slug: str, user: CurrentUser) -> StudioContext:
        studio = await get_studio_by_slug(slug)
        if not studio:
            raise HTTPException(404, "Studio not found")
        m = await db.memberships.find_one({"studio_id": studio.id, "user_id": user.id, "status": "active"})
        if not m or m["role"] not in roles:
            raise HTTPException(403, "You don't have access to this studio")
        return StudioContext(studio=studio, user=user, role=m["role"], membership_id=str(m["_id"]))
    return dep


StudioOwner = Annotated[StudioContext, Depends(studio_role("owner"))]
StudioMember = Annotated[StudioContext, Depends(studio_role("owner", "artist"))]
