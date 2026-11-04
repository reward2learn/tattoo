from datetime import datetime
from typing import Literal

from bson import ObjectId

from core.db import db
from core.models import BaseDocument, utcnow

AccountType = Literal["client", "artist", "studio_owner"]
ACCOUNT_TYPES = ("client", "artist", "studio_owner")


class User(BaseDocument):
    email: str
    name: str
    password_hash: str | None = None
    picture: str | None = None
    account_type: AccountType | None = None
    is_platform_admin: bool = False
    auth_providers: list[str] = []
    session_version: int = 0
    created_at: datetime


async def get_user(user_id: str) -> User | None:
    if not ObjectId.is_valid(user_id):
        return None
    return User.from_mongo(await db.users.find_one({"_id": ObjectId(user_id)}))


async def get_user_by_email(email: str) -> User | None:
    return User.from_mongo(await db.users.find_one({"email": email.strip().lower()}))


async def create_user(**fields) -> User:
    user = User(id=str(ObjectId()), created_at=utcnow(), **fields)
    await db.users.insert_one(user.to_mongo())
    return user


async def _memberships_view(user: User) -> list[dict]:
    rows = await db.memberships.find({"user_id": user.id, "status": "active"}).to_list(200)
    studio_ids = [ObjectId(r["studio_id"]) for r in rows]
    studios = {str(s["_id"]): s for s in await db.studios.find({"_id": {"$in": studio_ids}}).to_list(200)}
    out = []
    for r in rows:
        s = studios.get(r["studio_id"])
        if s:
            out.append({"membership_id": str(r["_id"]), "studio_id": r["studio_id"], "slug": s["slug"],
                        "name": s["name"], "role": r["role"], "city": s.get("city")})
    return out


def roles_for(user: User, memberships: list[dict]) -> list[str]:
    roles = set()
    if user.account_type == "client":
        roles.add("client")
    if user.account_type == "artist" or any(m["role"] == "artist" for m in memberships):
        roles.add("artist")
    if user.account_type == "studio_owner" or any(m["role"] == "owner" for m in memberships):
        roles.add("studio_owner")
    if user.is_platform_admin:
        roles.add("platform_admin")
    return sorted(roles)


async def user_view(user: User) -> dict:
    memberships = await _memberships_view(user)
    pending = await db.memberships.count_documents({"invited_email": user.email, "status": "invited"})
    return {
        "id": user.id, "email": user.email, "name": user.name, "picture": user.picture,
        "account_type": user.account_type, "is_platform_admin": user.is_platform_admin,
        "needs_account_type": user.account_type is None and not user.is_platform_admin,
        "roles": roles_for(user, memberships), "memberships": memberships, "pending_invitations": pending,
    }
