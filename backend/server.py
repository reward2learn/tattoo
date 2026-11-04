import asyncio
import logging
import os
from contextlib import suppress
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from fastapi import APIRouter, FastAPI, Request  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402

from core.db import client, ensure_indexes  # noqa: E402
from routes import auth, poc_ai, poc_email, poc_payments, public, studios  # noqa: E402
from services import seed, storage  # noqa: E402
from services.errors import ProviderError  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="InkForge API", version="phase-1", openapi_url="/api/openapi.json", docs_url="/api/docs",
              redoc_url=None)

health = APIRouter(prefix="/api", tags=["health"])


@health.get("/")
async def root():
    return {"service": "inkforge", "phase": 1}


@app.exception_handler(ProviderError)
async def provider_error_handler(_: Request, exc: ProviderError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": f"{exc.provider} failed: {exc.message}", "provider": exc.provider, "error": exc.message, **exc.extra},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError):
    errors = [{"loc": e.get("loc"), "msg": str(e.get("msg", "")).removeprefix("Value error, "), "type": e.get("type")}
              for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})


for r in (health, auth.router, studios.router, public.router, poc_ai.router, poc_payments.router, poc_email.router):
    app.include_router(r)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ["CORS_ORIGINS"].split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _boot() -> None:
    await ensure_indexes()
    try:
        await asyncio.to_thread(storage.init_storage)
        await seed.seed()
    except Exception as exc:
        logger.error("Startup storage/seed failed: %s", exc)


@app.on_event("startup")
async def startup():
    app.state.boot_task = asyncio.create_task(_boot())


@app.on_event("shutdown")
async def shutdown():
    app.state.boot_task.cancel()
    with suppress(asyncio.CancelledError):
        await app.state.boot_task
    client.close()
