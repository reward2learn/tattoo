# Phase 0 integration POC regression tests (JRN-1..JRN-20): chat, images, storage, Stripe, Connect, email, openapi
import io
import json
import os
import subprocess
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv
from PIL import Image
from pymongo import MongoClient

load_dotenv(Path("/app/frontend/.env"))
load_dotenv(Path("/app/backend/.env"))
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"
IMG_TIMEOUT = 240
mdb = MongoClient(os.environ["MONGO_URL"])[os.environ["DB_NAME"]]
PROMPT = "minimalist fine-line rose tattoo design, black ink on white"
TATTOO_WORDS = ("tattoo", "rose", "wrist", "line", "fine", "placement", "ink", "design")


# ---------- Chat (JRN-1..4) ----------
class TestChat:
    @pytest.mark.parametrize("model", ["Claude Sonnet 5.5", "GPT 5.5", "Gemini 3.1 Pro"])
    def test_chat_models(self, model):
        r = requests.post(f"{API}/poc/chat", json={"model": model, "message": "I want a small fine-line rose on my inner wrist"}, timeout=180)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["model"] == model
        assert isinstance(d["reply"], str) and len(d["reply"].strip()) > 20
        assert any(w in d["reply"].lower() for w in TATTOO_WORDS), d["reply"][:300]
        print(model, d.get("model_id"), d.get("latency_ms"), d["reply"][:120].replace("\n", " "))

    def test_unsupported_model(self):
        for path in ("chat", "chat/stream"):
            r = requests.post(f"{API}/poc/{path}", json={"model": "made-up-model", "message": "hi"}, timeout=30)
            assert r.status_code == 400, (path, r.text)
            assert r.json()["detail"] == "Unsupported model"

    def test_empty_message_422(self):
        r = requests.post(f"{API}/poc/chat", json={"model": "GPT 5.5", "message": "   "}, timeout=30)
        assert r.status_code == 422

    def test_stream(self):
        r = requests.post(f"{API}/poc/chat/stream", json={"model": "Claude Sonnet 5.5", "message": "Suggest a placement for a small rose tattoo, one sentence."},
                          stream=True, timeout=180)
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        body = r.text
        deltas = [json.loads(l[6:])["delta"] for l in body.splitlines() if l.startswith("data: ") and "delta" in l]
        assert len(deltas) >= 1 and "".join(deltas).strip(), body[:500]
        assert "event: done" in body, body[-300:]
        assert "event: error" not in body
        print("stream chunks:", len(deltas))


def _gen(engine, transparent=False):
    return requests.post(f"{API}/poc/images/generate",
                         json={"engine": engine, "prompt": PROMPT, "transparent_background": transparent}, timeout=IMG_TIMEOUT)


def _download(rec):
    r = requests.get(BASE_URL + rec["url"], timeout=60)
    assert r.status_code == 200, r.text[:200]
    assert r.headers["content-type"].startswith("image/"), r.headers["content-type"]
    return r


def _check_record(rec):
    assert rec["id"] and rec["storage_path"]
    assert rec["url"] == f"/api/poc/images/{rec['id']}/file"
    from bson import ObjectId
    doc = mdb.poc_images.find_one({"_id": ObjectId(rec["id"])})
    assert doc is not None
    assert doc["storage_path"] == rec["storage_path"]
    for k, v in doc.items():
        if isinstance(v, (bytes, bytearray)) or (isinstance(v, str) and len(v) > 5000):
            pytest.fail(f"poc_images doc field {k} holds blob/base64")
    r = _download(rec)
    img = Image.open(io.BytesIO(r.content))
    assert (img.width, img.height) == (rec["width"], rec["height"])  # JRN-12
    return r, img


# ---------- Images (JRN-5..12) ----------
class TestImages:
    state = {}

    def test_gpt_generate(self):
        r = _gen("GPT Image 1")
        assert r.status_code == 200, r.text
        rec = r.json()
        assert rec["engine_label"] == "GPT Image 1"
        resp, img = _check_record(rec)
        self.state["gpt"] = rec
        self.state["gpt_bytes"] = resp.content
        print("gpt", rec["model_id"], rec["content_type"], rec["width"], rec["height"], rec["latency_ms"])

    def test_gpt_transparent(self):
        r = _gen("GPT Image 1", True)
        assert r.status_code == 200, r.text
        rec = r.json()
        resp, img = _check_record(rec)
        assert img.format == "PNG"
        rgba = img.convert("RGBA")
        assert img.mode in ("RGBA", "LA", "P"), img.mode
        w, h = rgba.size
        corners = [rgba.getpixel(p)[3] for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
        print("transparent corners", corners, "reported", rec.get("corner_alpha"))
        assert corners == [0, 0, 0, 0]

    def test_nano_generate(self):
        r = _gen("Nano Banana")
        assert r.status_code == 200, r.text
        rec = r.json()
        assert rec["engine_label"] == "Gemini Nano Banana"
        _check_record(rec)
        print("nano", rec["content_type"], rec["width"], rec["height"])

    def test_nano_edit(self):
        src = self.state.get("gpt") or pytest.skip("no gpt image")
        r = requests.post(f"{API}/poc/images/{src['id']}/edit",
                          json={"engine": "Nano Banana", "instruction": "convert to black-and-grey shading"}, timeout=IMG_TIMEOUT)
        assert r.status_code == 200, r.text
        rec = r.json()
        assert rec["id"] != src["id"] and rec["storage_path"] != src["storage_path"]
        assert rec["source_image_id"] == src["id"]
        resp, _ = _check_record(rec)
        assert resp.content != self.state["gpt_bytes"]

    def test_fal_generate(self):
        r = _gen("fal.ai")
        assert r.status_code == 200, r.text
        rec = r.json()
        assert rec["model_id"] == "fal-ai/flux-2"
        _check_record(rec)
        print("fal", rec["content_type"], rec["width"], rec["height"])

    def test_auto_generate_and_edit(self):
        r = _gen("Auto")
        assert r.status_code == 200, r.text
        rec = r.json()
        assert rec["engine_label"] == "GPT Image 1"
        e = requests.post(f"{API}/poc/images/{rec['id']}/edit", json={"engine": "Auto", "instruction": "add a small leaf"}, timeout=IMG_TIMEOUT)
        assert e.status_code == 200, e.text
        assert e.json()["engine_label"] == "Gemini Nano Banana"

    def test_empty_prompt_422_no_doc(self):
        before = mdb.poc_images.count_documents({})
        for p in ("", "    "):
            r = requests.post(f"{API}/poc/images/generate", json={"engine": "GPT Image 1", "prompt": p}, timeout=30)
            assert r.status_code == 422
        assert mdb.poc_images.count_documents({}) == before

    def test_errors(self):
        r = requests.post(f"{API}/poc/images/generate", json={"engine": "dalle-9", "prompt": "x"}, timeout=30)
        assert r.status_code == 400 and "Unsupported engine" in r.json()["detail"]
        src = self.state.get("gpt")
        iid = src["id"] if src else "000000000000000000000000"
        r = requests.post(f"{API}/poc/images/{iid}/edit", json={"engine": "fal.ai", "instruction": "x"}, timeout=30)
        assert r.status_code == 400 and "does not support edits" in r.json()["detail"]
        for bad in ("000000000000000000000000", "notanid"):
            assert requests.get(f"{API}/poc/images/{bad}", timeout=30).status_code == 404
            assert requests.get(f"{API}/poc/images/{bad}/file", timeout=30).status_code == 404
            r = requests.post(f"{API}/poc/images/{bad}/edit", json={"engine": "Nano Banana", "instruction": "x"}, timeout=30)
            assert r.status_code == 404
        r = requests.post(f"{API}/poc/images/generate", json={"engine": "Nano Banana", "prompt": "x", "transparent_background": True}, timeout=30)
        assert r.status_code == 400


def _webhook(session_id, times, forge=False):
    cmd = ["python", "scripts/send_signed_webhook.py", session_id, str(times), BASE_URL] + (["--forge"] if forge else [])
    out = subprocess.run(cmd, cwd="/app/backend", capture_output=True, text=True, timeout=120)
    print(out.stdout, out.stderr)
    lines = [l.split(" ", 2) for l in out.stdout.strip().splitlines()]
    return [(int(s), body) for _, s, body in lines]


# ---------- Payments (JRN-13..15) ----------
class TestPayments:
    def test_checkout_forged_and_idempotent_webhooks(self):
        r = requests.post(f"{API}/poc/payments/checkout", json={"amount_cents": 1000, "currency": "usd"}, timeout=60)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["checkout_url"].startswith("https://checkout.stripe.com/")
        sid = d["session_id"]
        t = requests.get(f"{API}/poc/payments/transactions/{sid}", timeout=30).json()
        assert t["status"] == "initiated" and t["amount"] == 1000 and isinstance(t["amount"], int) and t["currency"] == "usd"
        assert "_id" not in t
        # forged
        res = _webhook(sid, 3, forge=True)
        assert len(res) == 3 and all(s == 400 for s, _ in res)
        t2 = requests.get(f"{API}/poc/payments/transactions/{sid}", timeout=30).json()
        assert t2["status"] == "initiated" and t2["updated_at"] == t["updated_at"]
        # valid x3
        res = _webhook(sid, 3)
        assert all(s == 200 for s, _ in res)
        bodies = [json.loads(b) for _, b in res]
        assert bodies[0]["applied"] is True and bodies[0]["duplicate"] is False
        assert all(b["duplicate"] is True for b in bodies[1:])
        evt = bodies[0]["event_id"]
        assert mdb.stripe_events.count_documents({"event_id": evt}) == 1
        t3 = requests.get(f"{API}/poc/payments/transactions/{sid}", timeout=30).json()
        assert t3["status"] == "paid" and t3["paid_event_id"] == evt

    def test_checkout_validation(self):
        assert requests.post(f"{API}/poc/payments/checkout", json={"amount_cents": 10}, timeout=30).status_code == 422
        assert requests.post(f"{API}/poc/payments/checkout", json={"amount_cents": 1000, "currency": "eur"}, timeout=30).status_code == 422
        assert requests.get(f"{API}/poc/payments/transactions/cs_test_nope", timeout=30).status_code == 404

    def test_webhook_missing_signature(self):
        r = requests.post(f"{API}/stripe/webhook", data="{}", headers={"Content-Type": "application/json"}, timeout=30)
        assert r.status_code == 400


# ---------- Connect (JRN-16/17), Email (JRN-19), OpenAPI (JRN-20) ----------
class TestMisc:
    def test_connect_account_expected_stripe_error(self):
        r = requests.post(f"{API}/poc/connect/accounts", json={"country": "US"}, timeout=60)
        print("connect", r.status_code, r.text)
        if r.status_code == 200:
            assert r.json()["account_id"].startswith("acct_")
            return
        d = r.json()
        assert d["provider"] == "Stripe"
        assert "signed up for Connect" in d["error"]
        assert d.get("stripe_request_id", "").startswith("req_")

    def test_onboarding_link_nonexistent(self):
        r = requests.post(f"{API}/poc/connect/accounts/acct_doesnotexist123/onboarding-link", timeout=60)
        print("onboarding", r.status_code, r.text)
        assert r.status_code in (400, 403, 404, 424)
        d = r.json()
        assert d["provider"] == "Stripe" and d["error"] and d.get("stripe_request_id")

    def test_email(self):
        r = requests.post(f"{API}/poc/email/test", json={"to": "delivered@resend.dev"}, timeout=60)
        assert r.status_code == 200, r.text
        assert r.json()["message_id"]
        print("email", r.json())
        r = requests.post(f"{API}/poc/email/test", json={"to": "someone@example.com"}, timeout=30)
        assert r.status_code == 403
        r = requests.post(f"{API}/poc/email/test", json={"to": "not-an-email"}, timeout=30)
        assert r.status_code == 422

    def test_openapi(self):
        r = requests.get(f"{API}/openapi.json", timeout=30)
        assert r.status_code == 200
        paths = set(r.json()["paths"])
        print(sorted(paths))
        expected = {"/api/poc/chat", "/api/poc/chat/stream", "/api/poc/chat/models", "/api/poc/images/generate",
                    "/api/poc/images/{image_id}/edit", "/api/poc/images/{image_id}", "/api/poc/images/{image_id}/file",
                    "/api/poc/images/engines", "/api/poc/payments/checkout", "/api/poc/payments/transactions/{session_id}",
                    "/api/stripe/webhook", "/api/poc/connect/accounts", "/api/poc/connect/accounts/{account_id}/onboarding-link",
                    "/api/poc/email/test"}
        assert expected <= paths, expected - paths
