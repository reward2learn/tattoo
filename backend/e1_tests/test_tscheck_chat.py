import pytest
@pytest.mark.parametrize("model", ["Claude Sonnet 5.5", "GPT 5.5", "Gemini 3.1 Pro"])
def test_chat(api, model):
    r = api.post("/poc/chat", json={"model": model, "message": "tscheck-chat: give one short tip for fine-line tattoo aftercare"})
    assert r.status_code == 200, r.text
    j = r.json(); assert j["model"] == model and len(j["reply"]) > 20, r.text[:300]
    print(model, r.text[:300])
def test_unknown(api):
    r = api.post("/poc/chat", json={"model": "made-up-model", "message": "hi"})
    assert r.status_code == 400 and "Unsupported model" in r.text, r.text
