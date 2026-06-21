"""
main.py  –  WonderTels Hub  AI Layer  (FastAPI)
════════════════════════════════════════════════

Run locally:
    uvicorn main:app --reload --port 8050

Swagger UI:   http://localhost:8050/docs
ReDoc:        http://localhost:8050/redoc
OpenAPI JSON: http://localhost:8050/openapi.json
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from core.config import get_settings
from core.exceptions import register_exception_handlers
from core.logging import logger, setup_logging
from models.schemas import HealthResponse
from routers import stories, voices

# ── Bootstrap ─────────────────────────────────────────────────────
settings = get_settings()
setup_logging("DEBUG" if settings.app_env != "production" else "INFO")

# ── Sentry ─────────────────────────────────────────────────────────
if settings.sentry_dsn and settings.app_env == "production":
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        send_default_pii=True,
        traces_sample_rate=0.2,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ],
        environment="production",
    )


def _join_url(host: str, port: int, path: str = "") -> str:
    normalized_path = f"/{path.lstrip('/')}" if path else ""
    return f"http://{host}:{port}{normalized_path}"


def _connection_summary() -> str:
    local_base = _join_url("localhost", settings.app_port)
    docs_url = f"{local_base}/docs"
    lines = [
        f"📡 API Docs: {docs_url}",
        f"🏠 Local:  {local_base}/ | Docs: {docs_url}",
    ]

    if settings.lan_host:
        lan_base = _join_url(settings.lan_host, settings.app_port)
        lines.append(f"🔗 LAN:    {lan_base}/ | Docs: {lan_base}/docs")

    if settings.tailscale_host:
        tailscale_base = _join_url(
            settings.tailscale_host,
            settings.app_port,
            settings.tailscale_path,
        )
        lines.append(
            f"🌐 Tailscale: {tailscale_base} | API Docs: {tailscale_base.rstrip('/')}/docs"
        )

    lines.append("   Share the LAN URL with teammates on the same network.")
    if settings.tailscale_host:
        lines.append(
            "   Share this URL with teammates on different networks via Tailscale."
        )

    return "\n".join(lines)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "wondertels.startup",
        env=settings.app_env,
        model=settings.openai_model,
        audio_dir=settings.audio_storage_dir,
    )
    print(_connection_summary())
    yield
    logger.info("wondertels.shutdown")


# ── App ────────────────────────────────────────────────────────────
app = FastAPI(
    title="WonderTels Hub – AI Layer",
    description=(
        "Production AI API powering story generation (OpenAI GPT-4o) "
        "and voice narration + cloning (ElevenLabs).\n\n"
        "### Quick start\n"
        "1. `POST /stories/generate` – generate + narrate a new story\n"
        "2. `POST /stories/continue` – continue an existing story\n"
        "3. `GET  /voices` – list available narrator voices\n"
        "4. `POST /voices/clone` – clone a family voice *(Premium)*\n"
    ),
    version="1.0.0",
    contact={"name": "WonderTels Engineering"},
    license_info={"name": "Proprietary"},
    openapi_tags=[
        {"name": "Stories", "description": "AI story generation and continuation"},
        {"name": "Voices", "description": "Preset voices and family voice cloning"},
        {"name": "System", "description": "Health checks and metadata"},
    ],
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ─────────────────────────────────────────────
register_exception_handlers(app)

# ── Static audio files ─────────────────────────────────────────────
_audio_dir = Path(settings.audio_storage_dir)
_audio_dir.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(_audio_dir)), name="audio")

# ── Routers ─────────────────────────────────────────────────────────
app.include_router(stories.router)
app.include_router(voices.router)


# ── System endpoints ─────────────────────────────────────────────────

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check",
)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.app_env)


@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse({"message": "WonderTels AI Layer – visit /docs for Swagger UI"})


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env != "production",
    )


