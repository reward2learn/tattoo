"""Phase 1 regression: auth, isolation/policy, studios, branding, team/invitations, platform tenants, openapi."""
import io
import os
import uuid

import pytest
import requests
from PIL import Image

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"
PW = "Tattoo123!"
S1, S2 = "kawi-ink-jakarta", "ombak-tattoo-bali"


def login(email, password=PW):
    s = requests.Session()
    r = s.post(f"{API}/auth/login", json={"email": email, "password": password})
    if r.status_code != 200:
        pytest.skip(f"login failed for {email}: {r.status_code} {r.text}")
    return s


def register(account_type, prefix="TEST_"):
    s = requests.Session()
    email = f"{prefix.lower()}{uuid.uuid4().hex[:8]}@example.com"
    r = s.post(f"{API}/auth/register", json={"name": f"TEST {account_type}", "email": email,
                                             "password": "Passw0rd!", "account_type": account_type})
    assert r.status_code == 200, r.text
    return s, email, r.json()


CREATED_STUDIO_IDS = []


@pytest.fixture(scope="module", autouse=True)
def cleanup_created_studios():
    """No studio delete API exists: remove only the studios (by id) this module created, plus their memberships."""
    yield
    if not CREATED_STUDIO_IDS:
        return
    from bson import ObjectId
    from dotenv import dotenv_values
    from pymongo import MongoClient
    env = dotenv_values("/app/backend/.env")
    db = MongoClient(env["MONGO_URL"])[env["DB_NAME"]]
    for sid in CREATED_STUDIO_IDS:
        db.studios.delete_one({"_id": ObjectId(sid)})
        db.memberships.delete_many({"studio_id": sid})


def create_studio(session, name, slug):
    r = session.post(f"{API}/studios", json={"name": name, "slug": slug})
    assert r.status_code == 200, r.text
    CREATED_STUDIO_IDS.append(r.json()["id"])
    return r.json()


def png_bytes(w=300, h=120, size=None):
    if size:  # large incompressible PNG
        img = Image.frombytes("RGB", (1600, 1400), os.urandom(1600 * 1400 * 3))
    else:
        img = Image.new("RGB", (w, h), (200, 40, 40))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


# ---------- OpenAPI / Phase 0 presence (JRN-58) ----------
class TestOpenAPI:
    def test_openapi_lists_phase1_and_poc(self):
        r = requests.get(f"{API}/openapi.json")
        assert r.status_code == 200
        paths = r.json()["paths"].keys()
        for p in ["/api/auth/register", "/api/auth/login", "/api/auth/refresh", "/api/auth/logout", "/api/auth/me",
                  "/api/studios", "/api/studios/{slug}/branding", "/api/studios/{slug}/logo",
                  "/api/studios/{slug}/team", "/api/studios/{slug}/invitations",
                  "/api/me/invitations/{invitation_id}/accept", "/api/platform/tenants"]:
            assert p in paths, p
        assert any(p.startswith("/api/poc/") for p in paths)


# ---------- Accounts ----------
class TestAuth:
    @pytest.mark.parametrize("t", ["client", "artist", "studio_owner"])
    def test_register_types_and_me(self, t):
        s, email, user = register(t)
        assert user["email"] == email and user["account_type"] == t
        assert "access_token" in s.cookies and "refresh_token" in s.cookies
        me = s.get(f"{API}/auth/me").json()
        assert me["email"] == email

    def test_duplicate_email(self):
        _, email, _ = register("client")
        r = requests.post(f"{API}/auth/register", json={"name": "x", "email": email, "password": "Passw0rd!",
                                                         "account_type": "client"})
        assert r.status_code == 409 and "already exists" in r.json()["detail"]

    def test_short_password(self):
        r = requests.post(f"{API}/auth/register", json={"name": "x", "email": f"test_{uuid.uuid4().hex[:6]}@example.com",
                                                         "password": "abc", "account_type": "client"})
        assert r.status_code == 422 and "at least 8" in str(r.json()["detail"])

    def test_wrong_password_fresh_user(self):
        _, email, _ = register("client")
        r = requests.post(f"{API}/auth/login", json={"email": email, "password": "WrongPass1!"})
        assert r.status_code == 401 and r.json()["detail"] == "Invalid email or password"

    def test_lockout_after_5_failures_fresh_user(self):
        _, email, _ = register("client")
        codes = [requests.post(f"{API}/auth/login", json={"email": email, "password": "bad-pass-x"}).status_code
                 for _ in range(6)]
        assert codes[:5] == [401] * 5 and codes[5] == 429

    def test_refresh_and_logout_ends_sessions(self):
        s, email, _ = register("client")
        other = requests.Session()
        assert other.post(f"{API}/auth/login", json={"email": email, "password": "Passw0rd!"}).status_code == 200
        r = s.post(f"{API}/auth/refresh")
        assert r.status_code == 200 and r.json()["refreshed"] is True
        assert s.post(f"{API}/auth/logout").status_code == 200
        assert s.get(f"{API}/auth/me").status_code == 401
        assert other.get(f"{API}/auth/me").status_code == 401  # session_version bump ends all sessions

    def test_bcrypt_hash(self):
        from pymongo import MongoClient
        from dotenv import dotenv_values
        env = dotenv_values("/app/backend/.env")
        u = MongoClient(env["MONGO_URL"])[env["DB_NAME"]].users.find_one({"email": "admin@inkforge.test"})
        assert u["password_hash"].startswith("$2b$")


# ---------- Isolation (Q-8, Q-9) ----------
class TestIsolation:
    @pytest.fixture(scope="class")
    def owner1(self):
        return login("owner.jakarta@inkforge.test")

    @pytest.fixture(scope="class")
    def artist1(self):
        return login("artist.dimas@inkforge.test")

    def test_owner1_cannot_touch_studio2(self, owner1):
        assert owner1.get(f"{API}/studios/{S2}/settings").status_code == 403
        assert owner1.patch(f"{API}/studios/{S2}/branding", json={"tagline": "hacked"}).status_code == 403
        assert owner1.get(f"{API}/studios/{S2}/team").status_code == 403
        assert owner1.post(f"{API}/studios/{S2}/invitations", json={"email": "x@example.com"}).status_code == 403
        assert owner1.get(f"{API}/studios/{S2}/audit").status_code == 403
        assert owner1.get(f"{API}/studios/{S2}/workspace").status_code == 403
        pub = requests.get(f"{API}/public/studios/{S2}").json()
        assert pub["tagline"] != "hacked"

    def test_tenant_id_injection_rejected(self, owner1):
        before = requests.get(f"{API}/public/studios/{S2}").json()
        r = owner1.patch(f"{API}/studios/{S1}/branding", json={"tagline": "x", "tenantId": "abc", "studio_id": "abc"})
        assert r.status_code == 422
        after = requests.get(f"{API}/public/studios/{S2}").json()
        assert before == after

    def test_artist_cannot_brand_or_invite(self, artist1):
        assert artist1.patch(f"{API}/studios/{S1}/branding", json={"tagline": "x"}).status_code == 403
        assert artist1.post(f"{API}/studios/{S1}/invitations", json={"email": "x@example.com"}).status_code == 403
        assert artist1.get(f"{API}/studios/{S1}/workspace").status_code == 200

    @pytest.mark.parametrize("method,path", [
        ("get", "/auth/me"), ("get", f"/studios/{S1}/settings"), ("patch", f"/studios/{S1}/branding"),
        ("post", f"/studios/{S1}/logo"), ("get", f"/studios/{S1}/team"), ("post", f"/studios/{S1}/invitations"),
        ("delete", f"/studios/{S1}/invitations/abc"), ("delete", f"/studios/{S1}/members/abc"),
        ("get", f"/studios/{S1}/audit"), ("get", f"/studios/{S1}/workspace"), ("get", "/me/invitations"),
        ("post", "/me/invitations/abc/accept"), ("post", "/me/invitations/abc/decline"),
        ("get", "/platform/tenants"), ("post", "/studios"), ("get", "/studios/slug-check?slug=abc"),
        ("post", "/auth/account-type"),
    ])
    def test_no_token_and_tampered_401(self, method, path):
        r = getattr(requests, method)(f"{API}{path}", json={})
        assert r.status_code == 401, (path, r.status_code)
        r = getattr(requests, method)(f"{API}{path}", json={}, headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ4In0.tampered"})
        assert r.status_code == 401, (path, r.status_code)


# ---------- Studio creation + branding ----------
class TestStudioCreateAndBranding:
    @pytest.fixture(scope="class")
    def studio(self):
        s, email, _ = register("studio_owner")
        slug = f"test-{uuid.uuid4().hex[:8]}"
        create_studio(s, "TEST Studio", slug)
        return s, slug

    @pytest.mark.parametrize("slug,msg", [("ab", "3–40"), ("Bad Slug!", "3–40"), ("kawi-ink-jakarta", "taken"),
                                          ("admin", "reserved")])
    def test_slug_check_errors(self, studio, slug, msg):
        s, _ = studio
        r = s.get(f"{API}/studios/slug-check", params={"slug": slug})
        assert r.status_code == 200 and r.json()["available"] is False and msg in r.json()["message"]

    def test_client_cannot_create_studio(self):
        s, _, _ = register("client")
        assert s.post(f"{API}/studios", json={"name": "TEST X", "slug": f"test-{uuid.uuid4().hex[:6]}"}).status_code == 403

    def test_create_taken_slug_409(self, studio):
        s, _ = studio
        r = s.post(f"{API}/studios", json={"name": "TEST dup", "slug": S1})
        assert r.status_code == 409

    def test_branding_update_and_public(self, studio):
        s, slug = studio
        r = s.patch(f"{API}/studios/{slug}/branding", json={"primary_color": "#1a1a1a", "accent_color": "#C8A96A",
                    "tagline": "TEST tag", "about": "TEST about", "city": "Bandung",
                    "contact_email": "hi@example.com", "instagram": "teststudio"})
        assert r.status_code == 200, r.text
        pub = requests.get(f"{API}/public/studios/{slug}").json()
        assert pub["primary_color"] == "#1A1A1A" and pub["instagram"] == "@teststudio" and pub["city"] == "Bandung"

    @pytest.mark.parametrize("bad", ["red", "#12"])
    def test_invalid_hex(self, studio, bad):
        s, slug = studio
        r = s.patch(f"{API}/studios/{slug}/branding", json={"primary_color": bad})
        assert r.status_code == 422 and "Enter a valid hex color like #1A1A1A" in str(r.json())

    def test_logo_png_ok(self, studio):
        s, slug = studio
        r = s.post(f"{API}/studios/{slug}/logo", files={"file": ("logo.png", png_bytes(), "image/png")})
        assert r.status_code == 200, r.text
        assert r.json()["logo_url"] and r.json()["logo_width"] == 300
        img = requests.get(f"{BASE_URL}{r.json()['logo_url']}")
        assert img.status_code == 200 and img.headers["content-type"] == "image/png"

    @pytest.mark.parametrize("name,ctype,data", [("a.gif", "image/gif", b"GIF89a\x01\x00\x01\x00\x00\x00\x00;"),
                                                 ("a.pdf", "application/pdf", b"%PDF-1.4 test")])
    def test_logo_bad_type(self, studio, name, ctype, data):
        s, slug = studio
        r = s.post(f"{API}/studios/{slug}/logo", files={"file": (name, data, ctype)})
        assert r.status_code == 400 and r.json()["detail"] == "Logo must be PNG, JPG or WebP"

    def test_logo_too_large(self, studio):
        s, slug = studio
        data = png_bytes(size="big")
        assert len(data) > 5 * 1024 * 1024
        r = s.post(f"{API}/studios/{slug}/logo", files={"file": ("big.png", data, "image/png")})
        assert r.status_code == 400 and r.json()["detail"] == "Logo must be 5 MB or smaller"

    def test_unknown_public_slug(self):
        r = requests.get(f"{API}/public/studios/no-such-studio-xyz")
        assert r.status_code == 404 and r.json()["detail"] == "Studio not found"


# ---------- Team / invitations / audit (on a fresh TEST studio, seed untouched) ----------
class TestTeam:
    @pytest.fixture(scope="class")
    def ctx(self):
        owner, _, _ = register("studio_owner")
        slug = f"test-team-{uuid.uuid4().hex[:6]}"
        create_studio(owner, "TEST Team Studio", slug)
        return {"owner": owner, "slug": slug}

    def test_full_team_flow(self, ctx):
        owner, slug = ctx["owner"], ctx["slug"]
        email = f"test_inv_{uuid.uuid4().hex[:6]}@example.com"
        r = owner.post(f"{API}/studios/{slug}/invitations", json={"email": email})
        assert r.status_code == 200 and r.json()["message"] == "Invite created — email could not be sent"
        team = owner.get(f"{API}/studios/{slug}/team").json()
        assert any(m["email"] == email for m in team["invited"])
        # duplicate pending
        assert owner.post(f"{API}/studios/{slug}/invitations", json={"email": email}).status_code == 409
        # sign up with invited email -> invitations -> accept
        a = requests.Session()
        assert a.post(f"{API}/auth/register", json={"name": "TEST Invitee", "email": email, "password": "Passw0rd!",
                                                    "account_type": "artist"}).status_code == 200
        invs = a.get(f"{API}/me/invitations").json()
        assert len(invs) == 1 and invs[0]["studio"]["slug"] == slug
        assert a.post(f"{API}/me/invitations/{invs[0]['id']}/accept").status_code == 200
        team = owner.get(f"{API}/studios/{slug}/team").json()
        member = next(m for m in team["active"] if m["email"] == email)
        roster = requests.get(f"{API}/public/studios/{slug}").json()["artists"]
        assert any(x["name"] == "TEST Invitee" for x in roster)
        assert a.get(f"{API}/studios/{slug}/workspace").json()["role"] == "artist"
        # already active
        r = owner.post(f"{API}/studios/{slug}/invitations", json={"email": email})
        assert r.status_code == 409 and r.json()["detail"] == "Already a member of this studio"
        # remove -> former, off roster, workspace 403
        assert owner.delete(f"{API}/studios/{slug}/members/{member['id']}").status_code == 200
        team = owner.get(f"{API}/studios/{slug}/team").json()
        assert any(m["email"] == email for m in team["former"])
        assert requests.get(f"{API}/public/studios/{slug}").json()["artists"] == []
        assert a.get(f"{API}/studios/{slug}/workspace").status_code == 403
        # decline flow
        assert owner.post(f"{API}/studios/{slug}/invitations", json={"email": email}).status_code == 200
        inv = a.get(f"{API}/me/invitations").json()[0]
        assert a.post(f"{API}/me/invitations/{inv['id']}/decline").status_code == 200
        assert a.get(f"{API}/me/invitations").json() == []
        # revoke flow
        r = owner.post(f"{API}/studios/{slug}/invitations", json={"email": email})
        assert owner.delete(f"{API}/studios/{slug}/invitations/{r.json()['invitation_id']}").status_code == 200
        assert a.get(f"{API}/me/invitations").json() == []
        # sole owner remove self
        own = owner.get(f"{API}/studios/{slug}/team").json()["active"][0]
        r = owner.delete(f"{API}/studios/{slug}/members/{own['id']}")
        assert r.status_code == 400 and r.json()["detail"] == "A studio needs at least one owner"
        # audit
        audit = owner.get(f"{API}/studios/{slug}/audit").json()
        actions = [x.get("action") for x in audit]
        for act, n in [("membership.invite", 3), ("membership.accept", 1), ("membership.remove", 1),
                       ("membership.decline", 1), ("membership.revoke", 1)]:
            assert actions.count(act) == n, (act, actions)

    def test_other_user_cannot_accept_invite(self, ctx):
        owner, slug = ctx["owner"], ctx["slug"]
        email = f"test_inv_{uuid.uuid4().hex[:6]}@example.com"
        inv_id = owner.post(f"{API}/studios/{slug}/invitations", json={"email": email}).json()["invitation_id"]
        intruder, _, _ = register("artist")
        assert intruder.post(f"{API}/me/invitations/{inv_id}/accept").status_code == 404


# ---------- Platform tenants ----------
class TestPlatform:
    def test_admin_lists_tenants(self):
        s = login("admin@inkforge.test", "InkAdmin2026!")
        rows = s.get(f"{API}/platform/tenants").json()
        k = next(r for r in rows if r["slug"] == S1)
        assert k["name"] == "Kawi Ink Collective" and k["owner"]["email"] == "owner.jakarta@inkforge.test"
        assert isinstance(k["active_artist_count"], int) and k["created_at"]

    def test_client_forbidden(self):
        s = login("client@inkforge.test")
        r = s.get(f"{API}/platform/tenants")
        assert r.status_code == 403 and r.json()["detail"] == "You don't have access to this page"
