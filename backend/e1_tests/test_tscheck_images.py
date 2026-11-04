import io, pytest
from PIL import Image
def _check(api, db, rec):
    from bson import ObjectId
    f = api.get(f"/poc/images/{rec['id']}/file")
    assert f.status_code == 200 and f.headers["content-type"].startswith("image/")
    im = Image.open(io.BytesIO(f.content))
    assert im.size == (rec["width"], rec["height"])
    doc = db.poc_images.find_one({"_id": ObjectId(rec["id"])})
    assert doc and all(not (isinstance(v, (str, bytes)) and len(v) > 2000) for v in doc.values())
    return im
@pytest.mark.parametrize("engine", ["GPT Image 1", "Nano Banana", "fal.ai"])
def test_generate(api, db, engine):
    r = api.post("/poc/images/generate", json={"engine": engine, "prompt": "tscheck-img minimal swallow tattoo flash"})
    assert r.status_code == 200, r.text
    rec = r.json(); assert rec["storage_path"] and rec["url"]
    _check(api, db, rec); print(engine, rec["engine"], rec["content_type"], rec["width"], rec["height"])
def test_transparent(api, db):
    r = api.post("/poc/images/generate", json={"engine": "GPT Image 1", "prompt": "tscheck-img small black star tattoo", "transparent_background": True})
    assert r.status_code == 200, r.text
    im = _check(api, db, r.json()).convert("RGBA")
    w, h = im.size
    assert Image.open(io.BytesIO(api.get(r.json()["url"].replace("/api", "")).content)).format == "PNG"
    assert all(im.getpixel(p)[3] == 0 for p in [(0,0),(w-1,0),(0,h-1),(w-1,h-1)])
def test_auto_and_edit(api, db):
    r = api.post("/poc/images/generate", json={"engine": "Auto", "prompt": "tscheck-img simple anchor tattoo"})
    assert r.status_code == 200, r.text; src = r.json(); assert src["engine"] == "gpt-image-1"
    e = api.post(f"/poc/images/{src['id']}/edit", json={"engine": "Auto", "instruction": "add a red rope around the anchor"})
    assert e.status_code == 200, e.text; ed = e.json()
    assert ed["engine"] == "nano-banana" and ed["storage_path"] != src["storage_path"]
    a = api.get(f"/poc/images/{src['id']}/file").content; b = api.get(f"/poc/images/{ed['id']}/file").content
    assert a != b; _check(api, db, ed)
def test_empty_prompt(api, db):
    before = db.poc_images.count_documents({"prompt": ""})
    r = api.post("/poc/images/generate", json={"engine": "Auto", "prompt": ""})
    assert r.status_code == 422
    assert db.poc_images.count_documents({"prompt": ""}) == before
