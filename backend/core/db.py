import logging
import os

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, IndexModel

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]

# One entry per collection: every field a route filters, sorts or dedupes on.
INDEXES: dict[str, list[IndexModel]] = {
    "poc_images": [
        IndexModel([("storage_path", ASCENDING)], name="storage_path", unique=True),
        IndexModel([("created_at", DESCENDING)], name="created_at_desc"),
    ],
    "payment_transactions": [
        IndexModel([("session_id", ASCENDING)], name="session_id", unique=True),
    ],
    "stripe_events": [
        IndexModel([("event_id", ASCENDING)], name="event_id", unique=True),
    ],
    "connected_accounts": [
        IndexModel([("account_id", ASCENDING)], name="account_id", unique=True),
    ],
    "transfers": [
        IndexModel([("transfer_id", ASCENDING)], name="transfer_id", unique=True),
    ],
    "email_logs": [
        IndexModel([("created_at", DESCENDING)], name="created_at_desc"),
    ],
    "users": [
        IndexModel([("email", ASCENDING)], name="email", unique=True),
    ],
    "login_attempts": [
        IndexModel([("identifier", ASCENDING)], name="identifier", unique=True),
    ],
    "studios": [
        IndexModel([("slug", ASCENDING)], name="slug", unique=True),
        IndexModel([("created_at", ASCENDING)], name="created_at"),
    ],
    "memberships": [
        IndexModel([("studio_id", ASCENDING), ("user_id", ASCENDING)], name="studio_user_active", unique=True,
                   partialFilterExpression={"status": "active"}),
        IndexModel([("studio_id", ASCENDING), ("invited_email", ASCENDING)], name="studio_email_invited",
                   unique=True, partialFilterExpression={"status": "invited"}),
        IndexModel([("user_id", ASCENDING), ("status", ASCENDING)], name="user_status"),
        IndexModel([("invited_email", ASCENDING), ("status", ASCENDING)], name="email_status"),
    ],
    "audit_logs": [
        IndexModel([("studio_id", ASCENDING), ("at", DESCENDING)], name="studio_at"),
    ],
}


async def ensure_indexes() -> None:
    for collection, models in INDEXES.items():
        for model in models:
            try:
                await db[collection].create_indexes([model])
            except Exception as exc:
                logging.getLogger(__name__).error("ensure_indexes(%s.%s): %s", collection, model.document["name"], exc)
