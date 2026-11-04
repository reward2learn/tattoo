import io
import re
import uuid
from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException
from PIL import Image
from pymongo.errors import DuplicateKeyError

from core.db import db
from core.models import BaseDocument, utcnow
from services import audit, storage

SLUG_RE = re.compile(r"^[a-z0-9-]{3,40}$")
RESERVED_SLUGS = {"admin", "api", "auth", "marketplace", "dashboard", "artist", "platform", "t", "settings"}
LOGO_FORMATS = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}
LOGO_MAX_BYTES = 5 * 1024 * 1024


class Studio(BaseDocument):
    name: str
    slug: str
    owner_user_id: str
    primary_color: str = "#0F0F0F"
    accent_color: str = "#C8A96A"
    tagline: str = ""
    about: str = ""
    city: str = ""
    contact_email: str = ""
    instagram: str = ""
    logo_path: str | None = None
    logo_content_type: str | None = None
    logo_width: int | None = None
    logo_height: int | None = None
    logo_version: int = 0
    status: str = "active"
    created_at: datetime
    updated_at: datetime


def slug_problem(slug: str) -> str | None:
    if not SLUG_RE.match(slug):
        return "Use 3–40 lowercase letters, numbers or hyphens"
    if slug in RESERVED_SLUGS:
        return "This studio URL is reserved"
    return None


async def slug_status(slug: str) -> str | None:
    problem = slug_problem(slug)
    if problem:
        return problem
    if await db.studios.find_one({"slug": slug}, {"_id": 1}):
        return "This studio URL is taken"
    return None


async def get_studio_by_slug(slug: str) -> Studio | None:
    return Studio.from_mongo(await db.studios.find_one({"slug": slug, "status": "active"}))


def logo_url(studio: Studio) -> str | None:
    return f"/api/public/studios/{studio.slug}/logo?v={studio.logo_version}" if studio.logo_path else None


def studio_view(studio: Studio) -> dict:
    data = studio.model_dump(exclude={"logo_path", "owner_user_id"})
    return {**data, "logo_url": logo_url(studio)}


async def create_studio(owner_id: str, name: str, slug: str, **branding) -> Studio:
    problem = await slug_status(slug)
    if problem:
        raise HTTPException(409 if problem.endswith("taken") else 422, problem)
    now = utcnow()
    studio = Studio(id=str(ObjectId()), name=name, slug=slug, owner_user_id=owner_id,
                    created_at=now, updated_at=now, **branding)
    try:
        await db.studios.insert_one(studio.to_mongo())
    except DuplicateKeyError:
        raise HTTPException(409, "This studio URL is taken")
    await db.memberships.insert_one({
        "studio_id": studio.id, "user_id": owner_id, "invited_email": None, "role": "owner",
        "status": "active", "invited_by": None, "joined_at": now, "left_at": None, "created_at": now,
    })
    await audit.record("studio.create", owner_id, studio.id, {"slug": slug})
    return studio


async def update_branding(studio: Studio, actor_id: str, changes: dict) -> Studio:
    if changes:
        await db.studios.update_one({"_id": ObjectId(studio.id)}, {"$set": {**changes, "updated_at": utcnow()}})
        await audit.record("studio.branding_update", actor_id, studio.id, {"fields": sorted(changes)})
    return Studio.from_mongo(await db.studios.find_one({"_id": ObjectId(studio.id)}))


def validate_logo(filename: str, content_type: str | None, data: bytes) -> tuple[str, Image.Image]:
    ext = (filename.rsplit(".", 1)[-1] if "." in filename else "").lower()
    if ext not in ("png", "jpg", "jpeg", "webp") and content_type not in LOGO_FORMATS.values():
        raise HTTPException(400, "Logo must be PNG, JPG or WebP")
    if len(data) > LOGO_MAX_BYTES:
        raise HTTPException(400, "Logo must be 5 MB or smaller")
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        img = Image.open(io.BytesIO(data))
    except Exception:
        raise HTTPException(400, "Logo must be PNG, JPG or WebP")
    if img.format not in LOGO_FORMATS:
        raise HTTPException(400, "Logo must be PNG, JPG or WebP")
    return LOGO_FORMATS[img.format], img


async def save_logo(studio: Studio, actor_id: str | None, filename: str, content_type: str | None, data: bytes) -> Studio:
    mime, img = validate_logo(filename, content_type, data)
    path = storage.build_path(f"studios/{studio.id}", f"logo-{uuid.uuid4()}.{mime.split('/')[1]}")
    result = await storage.put_object(path, data, mime)
    await db.studios.update_one({"_id": ObjectId(studio.id)}, {
        "$set": {"logo_path": result["path"], "logo_content_type": mime, "logo_width": img.width,
                 "logo_height": img.height, "updated_at": utcnow()},
        "$inc": {"logo_version": 1},
    })
    await audit.record("studio.logo_update", actor_id, studio.id, {"path": result["path"]})
    return Studio.from_mongo(await db.studios.find_one({"_id": ObjectId(studio.id)}))


async def public_roster(studio: Studio) -> list[dict]:
    rows = await db.memberships.find({"studio_id": studio.id, "status": "active", "role": "artist"}).to_list(500)
    users = await db.users.find({"_id": {"$in": [ObjectId(r["user_id"]) for r in rows]}}).to_list(500)
    return sorted(({"id": str(u["_id"]), "name": u["name"], "picture": u.get("picture")} for u in users),
                  key=lambda u: u["name"])
