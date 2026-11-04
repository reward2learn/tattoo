import logging
from html import escape

from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from core.db import db
from core.models import utcnow
from services import audit, email
from services.studios import Studio
from services.users import User, get_user_by_email

logger = logging.getLogger(__name__)
RESERVED_EMAIL_DOMAINS = ("example.com", "example.org", "example.net")
RESERVED_EMAIL_TLDS = (".test", ".example", ".invalid", ".localhost")


def _oid(value: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(404, "Not found")
    return ObjectId(value)


def _deliverable(address: str) -> bool:
    domain = address.rsplit("@", 1)[-1]
    return domain not in RESERVED_EMAIL_DOMAINS and not domain.endswith(RESERVED_EMAIL_TLDS)


async def team_view(studio: Studio) -> dict:
    rows = await db.memberships.find({"studio_id": studio.id}).sort("created_at", 1).to_list(1000)
    ids = [ObjectId(r["user_id"]) for r in rows if r.get("user_id")]
    users = {str(u["_id"]): u for u in await db.users.find({"_id": {"$in": ids}}).to_list(1000)}
    groups = {"active": [], "invited": [], "former": []}
    for r in rows:
        u = users.get(r.get("user_id") or "")
        groups[r["status"]].append({
            "id": str(r["_id"]), "role": r["role"], "status": r["status"],
            "email": u["email"] if u else r.get("invited_email"), "name": u["name"] if u else None,
            "user_id": r.get("user_id"), "joined_at": r.get("joined_at"), "left_at": r.get("left_at"),
            "created_at": r.get("created_at"),
        })
    return groups


async def _send_invite_email(studio: Studio, to: str, base_url: str) -> bool:
    if not _deliverable(to):
        logger.info("Invite email skipped for reserved domain: %s", to)
        return False
    link = f"{base_url}/invitations"
    html = (
        '<table role="presentation" width="100%"><tr><td style="padding:24px;font-family:Arial,sans-serif">'
        f"<p>You have been invited to join <strong>{escape(studio.name)}</strong> as an artist on "
        f"{escape(email.EMAIL_FROM_NAME)}.</p>"
        f'<p><a href="{escape(link)}">Open your invitations</a> to accept or decline.</p>'
        f'<p style="font-size:12px;color:#888">Sent by {escape(email.EMAIL_FROM_NAME)}. '
        "We never ask for your password or card details by email.</p></td></tr></table>"
    )
    try:
        await email.send_email(to=to, subject=f"Join {studio.name} on {email.EMAIL_FROM_NAME}", html=html,
                               template="studio_invite")
        return True
    except Exception as exc:
        logger.warning("Invite email failed for %s: %s", to, exc)
        return False


async def invite(studio: Studio, actor: User, address: str, base_url: str) -> dict:
    address = address.strip().lower()
    existing_user = await get_user_by_email(address)
    if existing_user and await db.memberships.find_one(
        {"studio_id": studio.id, "user_id": existing_user.id, "status": "active"}
    ):
        raise HTTPException(409, "Already a member of this studio")
    now = utcnow()
    doc = {"studio_id": studio.id, "user_id": None, "invited_email": address, "role": "artist",
           "status": "invited", "invited_by": actor.id, "joined_at": None, "left_at": None, "created_at": now}
    try:
        result = await db.memberships.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(409, "An invitation is already pending for this email")
    await audit.record("membership.invite", actor.id, studio.id,
                       {"membership_id": str(result.inserted_id), "email": address})
    sent = await _send_invite_email(studio, address, base_url)
    return {"invitation_id": str(result.inserted_id), "email": address, "email_sent": sent,
            "message": "Invitation sent" if sent else "Invite created — email could not be sent"}


async def my_invitations(user: User) -> list[dict]:
    rows = await db.memberships.find({"invited_email": user.email, "status": "invited"}).to_list(200)
    studios = {str(s["_id"]): s for s in await db.studios.find(
        {"_id": {"$in": [ObjectId(r["studio_id"]) for r in rows]}}).to_list(200)}
    return [{"id": str(r["_id"]), "role": r["role"], "created_at": r["created_at"],
             "studio": {"name": studios[r["studio_id"]]["name"], "slug": studios[r["studio_id"]]["slug"],
                        "city": studios[r["studio_id"]].get("city")}}
            for r in rows if r["studio_id"] in studios]


async def _my_invite(user: User, invitation_id: str) -> dict:
    row = await db.memberships.find_one({"_id": _oid(invitation_id), "status": "invited", "invited_email": user.email})
    if not row:
        raise HTTPException(404, "Invitation not found")
    return row


async def accept(user: User, invitation_id: str) -> dict:
    row = await _my_invite(user, invitation_id)
    if await db.memberships.find_one({"studio_id": row["studio_id"], "user_id": user.id, "status": "active"}):
        await db.memberships.delete_one({"_id": row["_id"]})
        raise HTTPException(409, "Already a member of this studio")
    await db.memberships.update_one({"_id": row["_id"]}, {"$set": {"user_id": user.id, "status": "active",
                                                                   "joined_at": utcnow()}})
    await audit.record("membership.accept", user.id, row["studio_id"], {"membership_id": str(row["_id"]),
                                                                        "user_id": user.id})
    return {"membership_id": str(row["_id"]), "status": "active"}


async def decline(user: User, invitation_id: str) -> dict:
    row = await _my_invite(user, invitation_id)
    await db.memberships.delete_one({"_id": row["_id"]})
    await audit.record("membership.decline", user.id, row["studio_id"], {"membership_id": str(row["_id"]),
                                                                         "email": user.email})
    return {"declined": True}


async def revoke(studio: Studio, actor: User, invitation_id: str) -> dict:
    row = await db.memberships.find_one({"_id": _oid(invitation_id), "studio_id": studio.id, "status": "invited"})
    if not row:
        raise HTTPException(404, "Invitation not found")
    await db.memberships.delete_one({"_id": row["_id"]})
    await audit.record("membership.revoke", actor.id, studio.id, {"membership_id": str(row["_id"]),
                                                                  "email": row["invited_email"]})
    return {"revoked": True}


async def remove(studio: Studio, actor: User, membership_id: str) -> dict:
    row = await db.memberships.find_one({"_id": _oid(membership_id), "studio_id": studio.id, "status": "active"})
    if not row:
        raise HTTPException(404, "Member not found")
    if row["role"] == "owner" and await db.memberships.count_documents(
        {"studio_id": studio.id, "role": "owner", "status": "active"}
    ) <= 1:
        raise HTTPException(400, "A studio needs at least one owner")
    await db.memberships.update_one({"_id": row["_id"]}, {"$set": {"status": "former", "left_at": utcnow()}})
    await audit.record("membership.remove", actor.id, studio.id, {"membership_id": str(row["_id"]),
                                                                  "user_id": row["user_id"]})
    return {"membership_id": str(row["_id"]), "status": "former"}
