from datetime import timedelta

import httpx
from fastapi import HTTPException

from core.db import db
from core.models import utcnow
from core.security import hash_password, verify_password
from services.users import ACCOUNT_TYPES, User, create_user, get_user_by_email

MAX_FAILED = 5
LOCKOUT = timedelta(minutes=15)
EMERGENT_SESSION_URL = "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data"


async def register(name: str, email: str, password: str, account_type: str) -> User:
    if account_type not in ACCOUNT_TYPES:
        raise HTTPException(422, "Choose an account type")
    if len(password) < 8:
        raise HTTPException(422, "Password must be at least 8 characters")
    email = email.strip().lower()
    if await get_user_by_email(email):
        raise HTTPException(409, "An account with this email already exists")
    return await create_user(email=email, name=name.strip(), password_hash=hash_password(password),
                             account_type=account_type, auth_providers=["password"])


def _aware(dt):
    from datetime import timezone
    return dt.replace(tzinfo=timezone.utc) if dt and dt.tzinfo is None else dt


async def login(email: str, password: str, ip: str) -> User:
    email = email.strip().lower()
    identifier = f"{ip}:{email}"
    attempt = await db.login_attempts.find_one({"identifier": identifier})
    if attempt and attempt.get("locked_until") and _aware(attempt["locked_until"]) > utcnow():
        raise HTTPException(429, "Too many failed attempts. Try again in 15 minutes")
    user = await get_user_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        count = (attempt or {}).get("count", 0) + 1
        update = {"count": count, "updated_at": utcnow()}
        if count >= MAX_FAILED:
            update.update(count=0, locked_until=utcnow() + LOCKOUT)
        await db.login_attempts.update_one({"identifier": identifier}, {"$set": update}, upsert=True)
        raise HTTPException(401, "Invalid email or password")
    await db.login_attempts.delete_one({"identifier": identifier})
    return user


async def google_exchange(session_id: str) -> User:
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(EMERGENT_SESSION_URL, headers={"X-Session-ID": session_id})
    if resp.status_code != 200:
        raise HTTPException(401, "Google sign-in failed")
    data = resp.json()
    email = data["email"].strip().lower()
    user = await get_user_by_email(email)
    if user:
        update = {"$addToSet": {"auth_providers": "google"}}
        if not user.picture and data.get("picture"):
            update["$set"] = {"picture": data["picture"]}
        await db.users.update_one({"email": email}, update)
        return await get_user_by_email(email)
    return await create_user(email=email, name=data.get("name") or email.split("@")[0],
                             picture=data.get("picture"), account_type=None, auth_providers=["google"])


async def set_account_type(user: User, account_type: str) -> User:
    if account_type not in ACCOUNT_TYPES:
        raise HTTPException(422, "Choose an account type")
    if user.account_type is not None:
        raise HTTPException(409, "Account type already chosen")
    await db.users.update_one({"email": user.email}, {"$set": {"account_type": account_type}})
    return await get_user_by_email(user.email)


async def end_sessions(user: User) -> None:
    await db.users.update_one({"email": user.email}, {"$inc": {"session_version": 1}})
