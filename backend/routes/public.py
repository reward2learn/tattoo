from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from core.db import db
from core.policy import PlatformAdmin
from services import storage, studios

router = APIRouter(prefix="/api", tags=["public", "platform"])


def _card(s: studios.Studio) -> dict:
    return {"name": s.name, "slug": s.slug, "city": s.city, "tagline": s.tagline,
            "primary_color": s.primary_color, "accent_color": s.accent_color, "logo_url": studios.logo_url(s)}


@router.get("/public/studios")
async def list_public_studios():
    rows = await db.studios.find({"status": "active"}).sort("created_at", 1).to_list(200)
    return [_card(studios.Studio.from_mongo(r)) for r in rows]


async def _studio(slug: str) -> studios.Studio:
    s = await studios.get_studio_by_slug(slug)
    if not s:
        raise HTTPException(404, "Studio not found")
    return s


@router.get("/public/studios/{slug}")
async def public_studio(slug: str):
    s = await _studio(slug)
    return {**_card(s), "about": s.about, "contact_email": s.contact_email, "instagram": s.instagram,
            "logo_width": s.logo_width, "logo_height": s.logo_height, "artists": await studios.public_roster(s)}


@router.get("/public/studios/{slug}/logo", response_class=Response)
async def studio_logo(slug: str):
    s = await _studio(slug)
    if not s.logo_path:
        raise HTTPException(404, "No logo")
    data, _ = await storage.get_object(s.logo_path)
    return Response(content=data, media_type=s.logo_content_type, headers={"Cache-Control": "public, max-age=86400"})


@router.get("/platform/tenants")
async def platform_tenants(_: PlatformAdmin):
    rows = await db.studios.find({}).sort("created_at", 1).to_list(1000)
    owners = {str(u["_id"]): u for u in await db.users.find(
        {"_id": {"$in": [ObjectId(r["owner_user_id"]) for r in rows]}}).to_list(1000)}
    out = []
    for r in rows:
        owner = owners.get(r["owner_user_id"], {})
        out.append({
            "id": str(r["_id"]), "name": r["name"], "slug": r["slug"], "status": r.get("status", "active"),
            "city": r.get("city"), "owner": {"name": owner.get("name"), "email": owner.get("email")},
            "active_artist_count": await db.memberships.count_documents(
                {"studio_id": str(r["_id"]), "role": "artist", "status": "active"}),
            "created_at": r["created_at"],
        })
    return out
