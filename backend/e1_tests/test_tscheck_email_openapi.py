def test_email(api):
    r = api.post("/poc/email/test", json={"to": "delivered@resend.dev"})
    assert r.status_code == 200 and "id" in r.text, r.text; print(r.text[:200])
def test_openapi(api):
    r = api.get("/openapi.json"); assert r.status_code == 200
    assert sum(p.startswith("/api/poc") for p in r.json()["paths"]) >= 10
def test_connect_verbatim(api):
    r = api.post("/poc/connect/accounts", json={"country": "US"})
    print(r.status_code, r.text[:300])
