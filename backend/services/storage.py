import asyncio
import os
import threading

import requests

from services.errors import ProviderError

STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or "https://integrations.emergentagent.com"
STORAGE_URL = STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
APP_NAME = os.environ["APP_NAME"]

_storage_key: str | None = None
_lock = threading.Lock()


def init_storage(force: bool = False) -> str:
    global _storage_key
    with _lock:
        if _storage_key and not force:
            return _storage_key
        resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": os.environ["EMERGENT_LLM_KEY"]}, timeout=30)
        resp.raise_for_status()
        _storage_key = resp.json()["storage_key"]
        return _storage_key


def _request(method: str, path: str, **kwargs) -> requests.Response:
    extra_headers = kwargs.pop("headers", {})
    for attempt in range(2):
        resp = requests.request(
            method, f"{STORAGE_URL}/objects/{path}",
            headers={"X-Storage-Key": init_storage(force=attempt == 1), **extra_headers},
            **kwargs,
        )
        if resp.status_code != 404 or attempt == 1 or method == "GET":
            break
    resp.raise_for_status()
    return resp


def _put(path: str, data: bytes, content_type: str) -> dict:
    return _request("PUT", path, data=data, headers={"Content-Type": content_type}, timeout=120).json()


def _get(path: str) -> tuple[bytes, str]:
    resp = _request("GET", path, timeout=60)
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")


async def put_object(path: str, data: bytes, content_type: str) -> dict:
    try:
        return await asyncio.to_thread(_put, path, data, content_type)
    except requests.RequestException as exc:
        raise ProviderError("Object Storage", str(exc)) from exc


async def get_object(path: str) -> tuple[bytes, str]:
    try:
        return await asyncio.to_thread(_get, path)
    except requests.RequestException as exc:
        raise ProviderError("Object Storage", str(exc)) from exc


def build_path(folder: str, filename: str) -> str:
    return f"{APP_NAME}/{folder}/{filename}"
