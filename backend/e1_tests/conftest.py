import io, os, subprocess, sys, httpx, pymongo, pytest
BASE = "http://localhost:8001/api"
@pytest.fixture(scope="session")
def api():
    with httpx.Client(base_url=BASE, timeout=240) as c:
        yield c
@pytest.fixture(scope="session")
def db():
    return pymongo.MongoClient(os.environ.get("MONGO_URL", "mongodb://localhost:27017"))["test_database"]
def webhook(session_id, times=1, forge=False):
    args = [sys.executable, "/app/backend/scripts/send_signed_webhook.py", session_id, str(times)] + (["--forge"] if forge else [])
    return subprocess.run(args, capture_output=True, text=True, timeout=120).stdout
