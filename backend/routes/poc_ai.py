import json
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel, Field, StringConstraints

from core.http import public_base_url
from services import images, llm_chat, storage
from services.errors import UnsupportedError
from services.image_engines import AUTO_ENGINE, ENGINES, resolve_engine

router = APIRouter(prefix="/api/poc", tags=["poc-ai"])

NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class ChatRequest(BaseModel):
    model: str = Field(examples=["Claude Sonnet 5.5"])
    message: NonEmpty
    session_id: str | None = None


def _model(name: str) -> llm_chat.ChatModel:
    try:
        return llm_chat.resolve_model(name)
    except UnsupportedError:
        raise HTTPException(400, "Unsupported model")


@router.get("/chat/models")
async def list_chat_models():
    return {"default": llm_chat.DEFAULT_CHAT_MODEL, "models": [m.__dict__ for m in llm_chat.CHAT_MODELS.values()]}


@router.post("/chat")
async def chat(req: ChatRequest):
    model = _model(req.model)
    result = await llm_chat.complete_reply(model, req.message, req.session_id)
    return {"model": model.display_name, "provider": model.provider_label, "model_id": model.model_id, **result}


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    model = _model(req.model)

    async def events():
        try:
            async for chunk in llm_chat.stream_reply(model, req.message, req.session_id):
                yield f"data: {json.dumps({'delta': chunk})}\n\n"
            yield "event: done\ndata: {}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'detail': str(exc)})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


class GenerateRequest(BaseModel):
    engine: str = Field("Auto", examples=["Auto", "GPT Image 1", "Nano Banana", "fal.ai"])
    prompt: NonEmpty
    transparent_background: bool = False


class EditRequest(BaseModel):
    engine: str = Field("Auto", examples=["Auto", "Nano Banana"])
    instruction: NonEmpty


def _engine(name: str, op: str):
    try:
        return resolve_engine(name, op)
    except UnsupportedError as exc:
        raise HTTPException(400, str(exc))


def _out(record: images.ImageRecord, request: Request) -> dict:
    path = f"/api/poc/images/{record.id}/file"
    return {**record.model_dump(), "url": path, "absolute_url": public_base_url(request) + path}


@router.get("/images/engines")
async def list_engines():
    return {"auto": AUTO_ENGINE, "engines": [
        {"key": e.key, "label": e.label, "model_id": e.model_id, "supports_edit": bool(e.edit),
         "supports_transparent": e.supports_transparent} for e in ENGINES.values()
    ]}


@router.post("/images/generate")
async def generate(req: GenerateRequest, request: Request):
    engine = _engine(req.engine, "generate")
    if req.transparent_background and not engine.supports_transparent:
        raise HTTPException(400, f"Engine {engine.label} does not support transparent background")
    return _out(await images.generate_image(engine, req.prompt, req.transparent_background), request)


async def _require(image_id: str) -> images.ImageRecord:
    record = await images.get_image(image_id)
    if not record:
        raise HTTPException(404, "Image not found")
    return record


@router.post("/images/{image_id}/edit")
async def edit(image_id: str, req: EditRequest, request: Request):
    engine = _engine(req.engine, "edit")
    source = await _require(image_id)
    return _out(await images.edit_image(engine, source, req.instruction), request)


@router.get("/images/{image_id}")
async def get_image(image_id: str, request: Request):
    return _out(await _require(image_id), request)


@router.get("/images/{image_id}/file", response_class=Response)
async def get_image_file(image_id: str):
    record = await _require(image_id)
    data, _ = await storage.get_object(record.storage_path)
    return Response(content=data, media_type=record.content_type, headers={"Cache-Control": "private, max-age=86400"})
