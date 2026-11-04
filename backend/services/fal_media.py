import os
import time
from typing import Any
from urllib.parse import urlparse

import requests

# Fal Universal Key supports queue inference through Emergent proxy, not Platform APIs.
INTEGRATION_PROXY_BASE = os.environ.get("INTEGRATION_PROXY_URL", "https://integrations.emergentagent.com").rstrip("/")
CONTROL_BASE = f"{INTEGRATION_PROXY_BASE}/api/v1/fal"
PUBLIC_QUEUE_BASE = f"{CONTROL_BASE}/queue"
QUEUE_ORIGIN = "https://queue.fal.run"


class UniversalMediaError(Exception):
    pass


class InsufficientCreditsError(UniversalMediaError):
    pass


def _headers(extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {"Authorization": f"Bearer {os.environ['EMERGENT_LLM_KEY']}", "Content-Type": "application/json"}
    job_id = os.environ.get("job_id")
    if job_id:
        headers["X-App-ID"] = job_id
        headers["X-Job-ID"] = job_id
    environment_id = os.environ.get("run_id")
    if environment_id:
        headers["X-Environment-ID"] = environment_id
    if extra:
        headers.update(extra)
    return headers


def _trusted_proxy_queue_url(value: str) -> str:
    candidate = urlparse(value)
    queue_base = urlparse(PUBLIC_QUEUE_BASE)
    if (
        candidate.scheme != queue_base.scheme
        or candidate.netloc != queue_base.netloc
        or candidate.username is not None
        or candidate.password is not None
        or candidate.fragment
        or not candidate.path.startswith(queue_base.path.rstrip("/") + "/")
    ):
        raise UniversalMediaError("Proxy returned an untrusted media queue URL")
    return value


def _get_with_retry(url: str, *, timeout_seconds: int, deadline: float, max_attempts: int = 5) -> requests.Response:
    delay_seconds = 1
    for attempt in range(max_attempts):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise UniversalMediaError("Timed out waiting for media generation")
        try:
            return requests.get(url, headers=_headers(), timeout=min(timeout_seconds, remaining))
        except (requests.ConnectTimeout, requests.ReadTimeout, requests.ConnectionError) as exc:
            if attempt == max_attempts - 1:
                raise UniversalMediaError("Media generation polling failed after transient network errors") from exc
            sleep_seconds = min(delay_seconds, deadline - time.monotonic())
            if sleep_seconds <= 0:
                raise UniversalMediaError("Timed out waiting for media generation") from exc
            time.sleep(sleep_seconds)
            delay_seconds *= 2
    raise AssertionError("unreachable")


def _raise_for(resp: requests.Response) -> None:
    if resp.status_code == 402:
        raise InsufficientCreditsError("Insufficient Universal Key credits for this generation")
    if not resp.ok:
        raise UniversalMediaError(f"HTTP {resp.status_code}: {resp.text[:500]}")


def run_media_generation(endpoint_id: str, payload: dict[str, Any], timeout_seconds: int = 600) -> dict[str, Any]:
    submit = requests.post(
        f"{CONTROL_BASE}/proxy",
        headers=_headers({"X-Fal-Target-Url": f"{QUEUE_ORIGIN}/{endpoint_id}"}),
        json=payload,
        timeout=60,
    )
    _raise_for(submit)
    submission = submit.json()
    status_url = _trusted_proxy_queue_url(submission["status_url"])
    response_url = _trusted_proxy_queue_url(submission["response_url"])

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        status_resp = _get_with_retry(status_url, timeout_seconds=30, deadline=deadline)
        _raise_for(status_resp)
        body = status_resp.json()
        status = (body.get("status") or "").upper()
        if status in {"COMPLETED", "OK"}:
            if body.get("error"):
                raise UniversalMediaError(f"Media generation failed: {body['error']}")
            result = _get_with_retry(response_url, timeout_seconds=60, deadline=deadline)
            _raise_for(result)
            return result.json()
        if status in {"FAILED", "CANCELLED", "CANCELED", "ERROR"}:
            raise UniversalMediaError(f"Media generation failed: {status}")
        time.sleep(2)
    raise UniversalMediaError("Timed out waiting for media generation")
