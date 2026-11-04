import asyncio
import base64
import os
import re
import uuid
from dataclasses import dataclass
from typing import Awaitable, Callable

import requests
from emergentintegrations.llm.chat import ImageContent, LlmChat, UserMessage
from emergentintegrations.llm.utils import get_integration_proxy_url
from litellm import aimage_generation

from services.errors import UnsupportedError
from services.fal_media import run_media_generation

TATTOO_STYLE = (
    "Tattoo flash design. Clean confident linework, single centered subject, plain background, "
    "no text, no lettering, no watermark, no skin or body. Subject: "
)

GenerateFn = Callable[[str, bool], Awaitable[bytes]]
EditFn = Callable[[bytes, str], Awaitable[bytes]]


GPT_IMAGE_MODEL_ID = os.environ["GPT_IMAGE_MODEL_ID"]


async def gpt_image_generate(prompt: str, transparent: bool) -> bytes:
    params = dict(
        model=f"openai/{GPT_IMAGE_MODEL_ID}",
        prompt=TATTOO_STYLE + prompt + (
            " Isolated on a fully transparent background." if transparent else " On a plain solid white background."
        ),
        n=1,
        size="1024x1024",
        quality="medium",
        api_key=os.environ["EMERGENT_LLM_KEY"],
        api_base=get_integration_proxy_url() + "/llm",
    )
    params.update(background="transparent" if transparent else "opaque", output_format="png")
    resp = await aimage_generation(**params)
    img = resp.data[0]
    if getattr(img, "b64_json", None):
        return base64.b64decode(img.b64_json)
    return (await asyncio.to_thread(requests.get, img.url, timeout=60)).content


NANO_BANANA_MODEL = "gemini-3.1-flash-image-preview"


async def _nano_banana(text: str, source: bytes | None) -> bytes:
    chat = LlmChat(
        api_key=os.environ["EMERGENT_LLM_KEY"],
        session_id=str(uuid.uuid4()),
        system_message="You are a tattoo design image generator. Always return an image.",
    ).with_model("gemini", NANO_BANANA_MODEL).with_params(modalities=["image", "text"])
    files = [ImageContent(base64.b64encode(source).decode())] if source else None
    _, images = await chat.send_message_multimodal_response(UserMessage(text=text, file_contents=files))
    if not images:
        raise RuntimeError("Provider returned no image")
    return base64.b64decode(images[0]["data"])


async def nano_banana_generate(prompt: str, transparent: bool) -> bytes:
    return await _nano_banana(TATTOO_STYLE + prompt, None)


async def nano_banana_edit(source: bytes, instruction: str) -> bytes:
    return await _nano_banana(
        f"Edit this tattoo design: {instruction}. Keep the same subject and composition, plain background, no text.",
        source,
    )


FAL_ENDPOINT = "fal-ai/flux-2"


async def fal_generate(prompt: str, transparent: bool) -> bytes:
    payload = {"prompt": TATTOO_STYLE + prompt, "image_size": "square_hd", "output_format": "png", "num_images": 1}
    result = await asyncio.to_thread(run_media_generation, FAL_ENDPOINT, payload)
    url = result["images"][0]["url"]
    resp = await asyncio.to_thread(requests.get, url, timeout=60)
    resp.raise_for_status()
    return resp.content


@dataclass(frozen=True)
class Engine:
    key: str
    label: str
    model_id: str
    generate: GenerateFn
    edit: EditFn | None = None
    supports_transparent: bool = False


ENGINES = {
    e.key: e
    for e in (
        Engine("gpt-image-1", "GPT Image 1", GPT_IMAGE_MODEL_ID, gpt_image_generate, supports_transparent=True),
        Engine("nano-banana", "Gemini Nano Banana", NANO_BANANA_MODEL, nano_banana_generate, nano_banana_edit),
        Engine("fal", "fal.ai", FAL_ENDPOINT, fal_generate),
    )
}

_ALIASES = {
    "gptimage1": "gpt-image-1", "openaigptimage1": "gpt-image-1",
    "nanobanana": "nano-banana", "gemininanobanana": "nano-banana",
    "fal": "fal", "falai": "fal",
}
AUTO_ENGINE = {"generate": "gpt-image-1", "edit": "nano-banana"}


def resolve_engine(name: str, operation: str) -> Engine:
    norm = re.sub(r"[^a-z0-9]", "", name.lower())
    key = AUTO_ENGINE[operation] if norm == "auto" else _ALIASES.get(norm)
    if not key:
        raise UnsupportedError("Unsupported engine")
    engine = ENGINES[key]
    if operation == "edit" and not engine.edit:
        raise UnsupportedError(f"Engine {engine.label} does not support edits")
    return engine
