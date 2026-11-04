import logging
import os
from pathlib import Path

from core.db import db
from core.models import utcnow
from core.security import hash_password
from services import studios
from services.users import create_user, get_user_by_email

logger = logging.getLogger(__name__)
ASSETS = Path(__file__).resolve().parents[1] / "seed_assets"

STUDIOS = [
    {"slug": "kawi-ink-jakarta", "name": "Kawi Ink Collective", "owner": "owner.jakarta@inkforge.test",
     "logo": "kawi_logo.jpg", "primary_color": "#0F0F0F", "accent_color": "#C8A96A",
     "tagline": "Fine-line and blackwork from the heart of Jakarta",
     "about": "Kawi Ink is a private fine-line and blackwork studio in Kemang, South Jakarta. Our artists blend "
              "Javanese ornament, botanical linework and modern minimalism. Every piece is drawn custom, "
              "consultations by appointment.",
     "city": "Jakarta", "contact_email": "hello@kawi-ink.test", "instagram": "@kawi.ink"},
    {"slug": "ombak-tattoo-bali", "name": "Ombak Tattoo House", "owner": "owner.bali@inkforge.test",
     "logo": "ombak_logo.jpg", "primary_color": "#123C3A", "accent_color": "#E07A5F",
     "tagline": "Ocean-born color work and neo-traditional in Canggu",
     "about": "Ombak Tattoo House sits two streets from Batu Bolong beach in Canggu, Bali. We specialise in "
              "neo-traditional, color realism and Balinese-inspired motifs, with a calm, sterile private studio.",
     "city": "Bali", "contact_email": "studio@ombak-tattoo.test", "instagram": "@ombak.tattoo"},
]

USERS = [
    ("owner.jakarta@inkforge.test", "Raka Pratama", "studio_owner"),
    ("owner.bali@inkforge.test", "Putu Ayu Lestari", "studio_owner"),
    ("artist.dimas@inkforge.test", "Dimas Saputra", "artist"),
    ("artist.sekar@inkforge.test", "Sekar Wulandari", "artist"),
    ("artist.wayan@inkforge.test", "Wayan Arta", "artist"),
    ("client@inkforge.test", "Nadia Kusuma", "client"),
]
ARTIST_STUDIO = {"artist.dimas@inkforge.test": "kawi-ink-jakarta", "artist.sekar@inkforge.test": "kawi-ink-jakarta",
                 "artist.wayan@inkforge.test": "ombak-tattoo-bali"}


async def _ensure_user(email: str, name: str, account_type: str | None, password: str, admin: bool = False):
    user = await get_user_by_email(email)
    if user:
        return user
    return await create_user(email=email, name=name, password_hash=hash_password(password),
                             account_type=account_type, is_platform_admin=admin, auth_providers=["password"])


async def seed() -> None:
    await _ensure_user(os.environ["ADMIN_EMAIL"], "Platform Admin", None, os.environ["ADMIN_PASSWORD"], admin=True)
    users = {e: await _ensure_user(e, n, t, os.environ["SEED_DEMO_PASSWORD"]) for e, n, t in USERS}
    for spec in STUDIOS:
        studio = await studios.get_studio_by_slug(spec["slug"])
        if not studio:
            fields = {k: spec[k] for k in ("primary_color", "accent_color", "tagline", "about", "city",
                                           "contact_email", "instagram")}
            studio = await studios.create_studio(users[spec["owner"]].id, spec["name"], spec["slug"], **fields)
        if not studio.logo_path:
            path = ASSETS / spec["logo"]
            await studios.save_logo(studio, None, path.name, None, path.read_bytes())
    for email, slug in ARTIST_STUDIO.items():
        studio = await studios.get_studio_by_slug(slug)
        user = users[email]
        if not await db.memberships.find_one({"studio_id": studio.id, "user_id": user.id}):
            now = utcnow()
            await db.memberships.insert_one({
                "studio_id": studio.id, "user_id": user.id, "invited_email": None, "role": "artist",
                "status": "active", "invited_by": None, "joined_at": now, "left_at": None, "created_at": now,
            })
    logger.info("Seed complete")
