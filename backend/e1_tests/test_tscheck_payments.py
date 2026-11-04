from conftest import webhook
def _checkout(api):
    r = api.post("/poc/payments/checkout", json={"amount_cents": 1000, "currency": "usd", "description": "tscheck-pay"})
    assert r.status_code == 200, r.text
    return r.json()
def test_checkout(api):
    d = _checkout(api); assert d["checkout_url"].startswith("https://checkout.stripe.com")
    t = api.get(f"/poc/payments/transactions/{d['session_id']}").json()
    assert t["status"] == "initiated" and t["amount"] == 1000 and t["currency"] == "usd", t
def test_forged_then_idempotent(api, db):
    sid = _checkout(api)["session_id"]
    out = webhook(sid, 1, forge=True); assert " 400 " in out, out
    assert api.get(f"/poc/payments/transactions/{sid}").json()["status"] == "initiated"
    out = webhook(sid, 3); assert out.count(" 200 ") == 3, out
    t = api.get(f"/poc/payments/transactions/{sid}").json()
    assert t["status"] == "paid", t
    assert db.stripe_events.count_documents({"id": t["paid_event_id"]}) + db.stripe_events.count_documents({"event_id": t["paid_event_id"]}) == 1
