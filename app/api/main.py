import logging
import os

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.services.errors import (
    ConflictError,
    DirectConversationExistsError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)


_logging_configured = False


def _configure_logging() -> None:
    global _logging_configured
    if _logging_configured:
        return
    level = os.environ.get("MESSENGER_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("messenger.log", encoding="utf-8"),
        ],
    )
    _logging_configured = True


def _error_body(code: str, message: str, **extra) -> dict:
    body = {"error": code, "message": message}
    body.update(extra)
    return body


def create_app() -> FastAPI:
    _configure_logging()
    log = logging.getLogger("messenger")
    app = FastAPI(title="Messenger Lab 2", version="0.1.0")

    @app.exception_handler(NotFoundError)
    async def _not_found(_: Request, exc: NotFoundError):
        log.warning("not found: %s", exc)
        return JSONResponse(status_code=404,
                            content=_error_body(exc.code, str(exc)))

    @app.exception_handler(ValidationError)
    async def _validation(_: Request, exc: ValidationError):
        log.warning("validation: %s", exc)
        return JSONResponse(status_code=400,
                            content=_error_body(exc.code, str(exc)))

    @app.exception_handler(ForbiddenError)
    async def _forbidden(_: Request, exc: ForbiddenError):
        log.warning("forbidden: %s", exc)
        return JSONResponse(status_code=403,
                            content=_error_body(exc.code, str(exc)))

    @app.exception_handler(DirectConversationExistsError)
    async def _direct_exists(_: Request, exc: DirectConversationExistsError):
        log.warning("conflict: %s", exc)
        return JSONResponse(
            status_code=409,
            content=_error_body(exc.code, str(exc), existingId=exc.existing_id),
        )

    @app.exception_handler(ConflictError)
    async def _conflict(_: Request, exc: ConflictError):
        log.warning("conflict: %s", exc)
        return JSONResponse(status_code=409,
                            content=_error_body(exc.code, str(exc)))

    @app.exception_handler(DomainError)
    async def _domain(_: Request, exc: DomainError):
        log.error("unhandled domain error: %s", exc, exc_info=True)
        return JSONResponse(status_code=500,
                            content=_error_body("internal_error",
                                                "Internal server error"))

    @app.exception_handler(RequestValidationError)
    async def _req_validation(_: Request, exc: RequestValidationError):
        log.warning("request validation: %s", exc)
        return JSONResponse(
            status_code=422,
            content=_error_body("validation_error",
                                "Request body is invalid",
                                details=exc.errors()),
        )

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    from app.api.routes import conversations, messages, users
    app.include_router(users.router)
    app.include_router(conversations.router)
    app.include_router(messages.router)

    return app
