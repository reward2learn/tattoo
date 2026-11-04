from core.db import db
from core.models import utcnow


async def record(action: str, actor_user_id: str | None, studio_id: str | None, target: dict) -> None:
    await db.audit_logs.insert_one({
        "action": action, "actor_user_id": actor_user_id, "studio_id": studio_id,
        "target": target, "at": utcnow(),
    })


async def list_for_studio(studio_id: str, limit: int = 200) -> list[dict]:
    rows = await db.audit_logs.find({"studio_id": studio_id}).sort("at", -1).to_list(limit)
    return [{**{k: v for k, v in r.items() if k != "_id"}, "id": str(r["_id"])} for r in rows]
