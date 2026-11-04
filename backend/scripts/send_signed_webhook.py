"""Deliver a Stripe-signed checkout.session.completed event for SESSION_ID to the webhook N times.

Usage: python scripts/send_signed_webhook.py <session_id> [times=2] [base_url] [--forge]
"""
import hashlib
import hmac
import json
import os
import sys
import time
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

session_id = sys.argv[1]
times = int(sys.argv[2]) if len(sys.argv) > 2 else 2
base = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else "http://localhost:8001"
forge = "--forge" in sys.argv

event = {
    "id": f"evt_poc_{uuid.uuid4().hex[:20]}",
    "object": "event",
    "type": "checkout.session.completed",
    "data": {"object": {"id": session_id, "object": "checkout.session", "payment_status": "paid", "status": "complete"}},
}
payload = json.dumps(event)
secret = "whsec_forged_secret" if forge else os.environ["STRIPE_WEBHOOK_SECRET"]
for i in range(times):
    ts = int(time.time())
    sig = hmac.new(secret.encode(), f"{ts}.{payload}".encode(), hashlib.sha256).hexdigest()
    r = requests.post(f"{base}/api/stripe/webhook", data=payload,
                      headers={"Content-Type": "application/json", "Stripe-Signature": f"t={ts},v1={sig}"}, timeout=30)
    print(i + 1, r.status_code, r.text)
