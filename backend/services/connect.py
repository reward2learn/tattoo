from datetime import datetime

import stripe

from core.db import db
from core.models import BaseDocument, utcnow
from services.stripe_client import call_stripe


class ConnectedAccount(BaseDocument):
    account_id: str
    type: str
    country: str | None = None
    email: str | None = None
    charges_enabled: bool = False
    payouts_enabled: bool = False
    details_submitted: bool = False
    created_at: datetime
    updated_at: datetime


class Transfer(BaseDocument):
    transfer_id: str
    destination: str
    amount: int  # cents
    currency: str
    created_at: datetime


def _status(acct) -> dict:
    return {
        "account_id": acct.id,
        "charges_enabled": bool(acct.charges_enabled),
        "payouts_enabled": bool(acct.payouts_enabled),
        "details_submitted": bool(acct.details_submitted),
        "requirements_currently_due": list((acct.requirements or {}).get("currently_due") or []),
        "capabilities": dict(acct.capabilities or {}),
    }


async def create_express_account(country: str | None, email: str | None) -> dict:
    kwargs = {"type": "express", "capabilities": {"transfers": {"requested": True}, "card_payments": {"requested": True}}}
    if country:
        kwargs["country"] = country
    if email:
        kwargs["email"] = email
    acct = await call_stripe(stripe.Account.create, **kwargs)
    now = utcnow()
    record = ConnectedAccount(
        account_id=acct.id, type="express", country=acct.country, email=email,
        charges_enabled=bool(acct.charges_enabled), payouts_enabled=bool(acct.payouts_enabled),
        details_submitted=bool(acct.details_submitted), created_at=now, updated_at=now,
    )
    await db.connected_accounts.insert_one(record.to_mongo())
    return _status(acct)


async def create_onboarding_link(account_id: str, refresh_url: str, return_url: str) -> dict:
    link = await call_stripe(
        stripe.AccountLink.create, account=account_id, refresh_url=refresh_url,
        return_url=return_url, type="account_onboarding",
    )
    return {"account_id": account_id, "url": link.url, "expires_at": link.expires_at}


async def get_account_status(account_id: str) -> dict:
    acct = await call_stripe(stripe.Account.retrieve, id=account_id)
    status = _status(acct)
    await db.connected_accounts.update_one(
        {"account_id": account_id},
        {"$set": {k: status[k] for k in ("charges_enabled", "payouts_enabled", "details_submitted")} | {"updated_at": utcnow()}},
    )
    return status


async def create_transfer(account_id: str, amount_cents: int, currency: str) -> dict:
    tr = await call_stripe(
        stripe.Transfer.create, amount=amount_cents, currency=currency, destination=account_id,
        metadata={"source": "inkforge-poc"},
    )
    record = Transfer(transfer_id=tr.id, destination=account_id, amount=tr.amount, currency=tr.currency, created_at=utcnow())
    await db.transfers.insert_one(record.to_mongo())
    return {"transfer_id": tr.id, "destination": account_id, "amount": tr.amount, "currency": tr.currency}
