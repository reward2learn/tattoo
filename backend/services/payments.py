from datetime import datetime

import stripe
from pymongo.errors import DuplicateKeyError

from core.db import db
from core.models import BaseDocument, utcnow
from services.stripe_client import STRIPE_WEBHOOK_SECRET, call_stripe


class PaymentTransaction(BaseDocument):
    session_id: str
    amount: int  # minor units (cents)
    currency: str
    description: str
    status: str  # initiated | paid | expired | failed
    payment_status: str
    stripe_payment_intent_id: str | None = None
    paid_event_id: str | None = None
    created_at: datetime
    updated_at: datetime
    paid_at: datetime | None = None


class StripeEvent(BaseDocument):
    event_id: str
    type: str
    session_id: str | None = None
    applied: bool
    processed_at: datetime


async def _create_session(**kwargs):
    # Tax: Stripe manages tax (managed payments); fall back to Stripe Tax calculation if ineligible.
    try:
        return await call_stripe(stripe.checkout.Session.create, **kwargs, managed_payments={"enabled": True})
    except Exception as exc:
        msg = str(exc).lower()
        if "managed payments" not in msg and "ineligible" not in msg:
            raise
        return await call_stripe(
            stripe.checkout.Session.create, **kwargs,
            automatic_tax={"enabled": True}, billing_address_collection="required",
        )


async def create_checkout(amount_cents: int, currency: str, description: str, base_url: str) -> tuple[PaymentTransaction, str]:
    session = await _create_session(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": currency,
                "product_data": {"name": description, "tax_code": "txcd_10000000"},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }],
        success_url=f"{base_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{base_url}/payment/cancel",
        metadata={"source": "inkforge-poc"},
    )
    now = utcnow()
    txn = PaymentTransaction(
        session_id=session.id, amount=amount_cents, currency=currency, description=description,
        status="initiated", payment_status="pending", created_at=now, updated_at=now,
    )
    result = await db.payment_transactions.insert_one(txn.to_mongo())
    txn.id = str(result.inserted_id)
    return txn, session.url


async def get_transaction(session_id: str) -> PaymentTransaction | None:
    return PaymentTransaction.from_mongo(await db.payment_transactions.find_one({"session_id": session_id}))


def verify_webhook(payload: bytes, signature: str) -> dict:
    """Raises ValueError / SignatureVerificationError on bad payload or signature."""
    return stripe.Webhook.construct_event(payload, signature, STRIPE_WEBHOOK_SECRET)


_STATUS_BY_EVENT = {
    "checkout.session.completed": ("paid", "paid"),
    "checkout.session.async_payment_succeeded": ("paid", "paid"),
    "checkout.session.async_payment_failed": ("failed", "failed"),
    "checkout.session.expired": ("expired", "expired"),
}


async def _apply(event: dict) -> bool:
    target = _STATUS_BY_EVENT.get(event["type"])
    if not target:
        return False
    obj = event["data"]["object"]
    if target[0] == "paid" and obj.get("payment_status") not in ("paid", "no_payment_required"):
        return False
    now = utcnow()
    update = {"status": target[0], "payment_status": target[1], "updated_at": now}
    if target[0] == "paid":
        update.update(paid_at=now, paid_event_id=event["id"], stripe_payment_intent_id=obj.get("payment_intent"))
    res = await db.payment_transactions.update_one(
        {"session_id": obj["id"], "status": {"$ne": "paid"}}, {"$set": update}
    )
    return res.modified_count == 1


async def process_event(event: dict) -> dict:
    obj = event.get("data", {}).get("object", {})
    record = StripeEvent(
        event_id=event["id"], type=event["type"],
        session_id=obj.get("id") if obj.get("object") == "checkout.session" else None,
        applied=False, processed_at=utcnow(),
    )
    try:
        await db.stripe_events.insert_one(record.to_mongo())
    except DuplicateKeyError:
        return {"event_id": event["id"], "duplicate": True, "applied": False}
    try:
        applied = await _apply(event)
    except Exception:
        await db.stripe_events.delete_one({"event_id": event["id"]})  # let Stripe's retry reprocess
        raise
    await db.stripe_events.update_one({"event_id": event["id"]}, {"$set": {"applied": applied}})
    return {"event_id": event["id"], "duplicate": False, "applied": applied}
