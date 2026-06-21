"""core/exceptions.py  –  Application-level exceptions + FastAPI handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class WonderTelsError(Exception):
    """Base error."""
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.detail


class StoryGenerationError(WonderTelsError):
    status_code = 502
    detail = "Failed to generate story from AI provider."


class NarrationError(WonderTelsError):
    status_code = 502
    detail = "Failed to generate narration audio."


class VoiceCloningError(WonderTelsError):
    status_code = 502
    detail = "Failed to clone voice."


class VoiceNotFoundError(WonderTelsError):
    status_code = 404
    detail = "Preset voice not found."


class InvalidInputError(WonderTelsError):
    status_code = 422
    detail = "Invalid input provided."


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(WonderTelsError)
    async def wondertels_handler(request: Request, exc: WonderTelsError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "type": type(exc).__name__},
        )
