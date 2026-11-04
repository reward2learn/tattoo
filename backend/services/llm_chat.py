import os
import time
import uuid
from dataclasses import dataclass
from typing import AsyncIterator

from emergentintegrations.llm.chat import LlmChat, StreamDone, TextDelta, UserMessage

from services.errors import ProviderError, UnsupportedError


@dataclass(frozen=True)
class ChatModel:
    display_name: str
    provider: str
    provider_label: str
    model_id: str


CHAT_MODELS = {
    m.display_name: m
    for m in (
        ChatModel("Claude Sonnet 5.5", "anthropic", "Anthropic", "claude-sonnet-5-5"),
        ChatModel("GPT 5.5", "openai", "OpenAI", "gpt-5.5"),
        ChatModel("Gemini 3.1 Pro", "gemini", "Google Gemini", "gemini-3.1-pro-preview"),
    )
}
DEFAULT_CHAT_MODEL = "Claude Sonnet 5.5"

TATTOO_SYSTEM_PROMPT = (
    "You are InkForge's tattoo consultation assistant. Help clients shape tattoo ideas: "
    "style, placement, size, color, linework and references. Be concise and practical."
)


def resolve_model(name: str) -> ChatModel:
    model = CHAT_MODELS.get(name)
    if not model:
        raise UnsupportedError("Unsupported model")
    return model


def _build_chat(model: ChatModel, session_id: str, system_message: str) -> LlmChat:
    return LlmChat(
        api_key=os.environ["EMERGENT_LLM_KEY"], session_id=session_id, system_message=system_message
    ).with_model(model.provider, model.model_id)


async def stream_reply(
    model: ChatModel, message: str, session_id: str | None = None, system_message: str = TATTOO_SYSTEM_PROMPT
) -> AsyncIterator[str]:
    chat = _build_chat(model, session_id or str(uuid.uuid4()), system_message)
    try:
        async for event in chat.stream_message(UserMessage(text=message)):
            if isinstance(event, TextDelta):
                yield event.content
            elif isinstance(event, StreamDone):
                break
    except Exception as exc:
        raise ProviderError(f"{model.provider_label} ({model.display_name})", str(exc)) from exc


async def complete_reply(model: ChatModel, message: str, session_id: str | None = None) -> dict:
    started = time.monotonic()
    reply = "".join([chunk async for chunk in stream_reply(model, message, session_id)])
    if not reply.strip():
        raise ProviderError(f"{model.provider_label} ({model.display_name})", "Empty reply from provider")
    return {"reply": reply, "latency_ms": int((time.monotonic() - started) * 1000)}
