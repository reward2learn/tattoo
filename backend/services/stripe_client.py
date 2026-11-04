import asyncio
import os
from typing import Any, Callable

import stripe

from services.errors import ProviderError

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]
STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]


async def call_stripe(fn: Callable[..., Any], **kwargs) -> Any:
    """Run a blocking Stripe SDK call; surface Stripe's error message verbatim."""
    try:
        return await asyncio.to_thread(fn, **kwargs)
    except stripe.error.StripeError as exc:
        err = getattr(exc, "error", None)
        raise ProviderError(
            "Stripe",
            (getattr(err, "message", None) or exc.user_message or str(exc)),
            status_code=exc.http_status if exc.http_status and exc.http_status < 500 else 424,
            extra={"stripe_code": exc.code, "stripe_request_id": exc.request_id, "stripe_http_status": exc.http_status},
        ) from exc
