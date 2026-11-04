import io
import time
import uuid
from datetime import datetime
from typing import Literal

from bson import ObjectId
from PIL import Image

from core.db import db
from core.models import BaseDocument, PyObjectId, utcnow
from services import storage
from services.errors import ProviderError
from services.image_engines import Engine


class ImageRecord(BaseDocument):
    engine: str
    engine_label: str
    model_id: str
    operation: Literal["generate", "edit"]
    prompt: str
    source_image_id: PyObjectId | None = None
    transparent_requested: bool = False
    storage_path: str
    content_type: str
    width: int
    height: int
    size_bytes: int
    has_alpha: bool
    corner_alpha: list[int] | None = None
    latency_ms: int
    is_deleted: bool = False
    created_at: datetime


def _inspect(data: bytes) -> dict:
    img = Image.open(io.BytesIO(data))
    fmt = (img.format or "PNG").lower()
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    corners = None
    if has_alpha:
        rgba = img.convert("RGBA")
        w, h = rgba.size
        corners = [rgba.getpixel(p)[3] for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    return {
        "content_type": f"image/{'jpeg' if fmt == 'jpg' else fmt}",
        "ext": "jpg" if fmt in ("jpeg", "jpg") else fmt,
        "width": img.width, "height": img.height,
        "has_alpha": has_alpha, "corner_alpha": corners,
    }


async def _store(engine: Engine, data: bytes, **fields) -> ImageRecord:
    try:
        meta = _inspect(data)
    except Exception as exc:
        raise ProviderError(f"Engine {engine.label}", f"Provider returned non-image data: {exc}") from exc
    path = storage.build_path("images", f"{uuid.uuid4()}.{meta.pop('ext')}")
    result = await storage.put_object(path, data, meta["content_type"])
    record = ImageRecord(
        id=str(ObjectId()), engine=engine.key, engine_label=engine.label, model_id=engine.model_id,
        storage_path=result["path"], size_bytes=len(data), created_at=utcnow(), **meta, **fields,
    )
    await db.poc_images.insert_one(record.to_mongo())
    return record


async def _call(engine: Engine, coro) -> bytes:
    try:
        return await coro
    except Exception as exc:
        raise ProviderError(f"Engine {engine.label}", str(exc)[:1000]) from exc


async def generate_image(engine: Engine, prompt: str, transparent: bool) -> ImageRecord:
    started = time.monotonic()
    data = await _call(engine, engine.generate(prompt, transparent))
    return await _store(
        engine, data, operation="generate", prompt=prompt, transparent_requested=transparent,
        latency_ms=int((time.monotonic() - started) * 1000),
    )


async def edit_image(engine: Engine, source: ImageRecord, instruction: str) -> ImageRecord:
    started = time.monotonic()
    original, _ = await storage.get_object(source.storage_path)
    data = await _call(engine, engine.edit(original, instruction))
    return await _store(
        engine, data, operation="edit", prompt=instruction, source_image_id=source.id,
        latency_ms=int((time.monotonic() - started) * 1000),
    )


async def get_image(image_id: str) -> ImageRecord | None:
    if not ObjectId.is_valid(image_id):
        return None
    return ImageRecord.from_mongo(await db.poc_images.find_one({"_id": ObjectId(image_id), "is_deleted": False}))
