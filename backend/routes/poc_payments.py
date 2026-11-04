import logging

import stripe
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

from core.http import public_base_url
from services import connect, payments

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["poc-payments"])


class CheckoutRequest(BaseModel):
    amount_cents: int = Field(ge=50, le=1_000_000, examples=[1000])
    currency: str = Field("usd", pattern="^usd$")
    description: str = Field("InkForge POC payment", max_length=120)


@router.post("/poc/payments/checkout")
async def create_checkout(req: CheckoutRequest, request: Request):
    txn, url = await payments.create_checkout(req.amount_cents, req.currency, req.description, public_base_url(request))
    return {"checkout_url": url, "session_id": txn.session_id, "transaction": txn.model_dump()}


@router.get("/poc/payments/transactions/{session_id}")
async def get_transaction(session_id: str):
    txn = await payments.get_transaction(session_id)
    if not txn:
        raise HTTPException(404, "Transaction not found")
    return txn.model_dump()


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    try:
        event = payments.verify_webhook(payload, request.headers.get("stripe-signature", ""))
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(400, "Invalid signature")
    result = await payments.process_event(event)
    logger.info("stripe webhook %s %s", event["type"], result)
    return {"status": "ok", **result}


class ConnectAccountRequest(BaseModel):
    country: str | None = Field(None, min_length=2, max_length=2, examples=["US"])
    email: str | None = None


class TransferRequest(BaseModel):
    account_id: str = Field(pattern="^acct_")
    amount_cents: int = Field(ge=1, le=100_000, examples=[100])
    currency: str = Field("usd", pattern="^usd$")


@router.post("/poc/connect/accounts")
async def create_connect_account(req: ConnectAccountRequest):
    return await connect.create_express_account(req.country, req.email)


def _link_urls(request: Request, account_id: str) -> tuple[str, str]:
    base = f"{public_base_url(request)}/api/poc/connect/accounts/{account_id}"
    return f"{base}/onboarding-refresh", base


@router.post("/poc/connect/accounts/{account_id}/onboarding-link")
async def create_onboarding_link(account_id: str, request: Request):
    return await connect.create_onboarding_link(account_id, *_link_urls(request, account_id))


@router.get("/poc/connect/accounts/{account_id}/onboarding-refresh", include_in_schema=False)
async def refresh_onboarding_link(account_id: str, request: Request):
    link = await connect.create_onboarding_link(account_id, *_link_urls(request, account_id))
    return RedirectResponse(link["url"])


@router.get("/poc/connect/accounts/{account_id}")
async def get_connect_account(account_id: str):
    return await connect.get_account_status(account_id)


@router.post("/poc/connect/transfers")
async def create_transfer(req: TransferRequest):
    return await connect.create_transfer(req.account_id, req.amount_cents, req.currency)
