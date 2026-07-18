"""Structured API errors and FastAPI exception handlers."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def handle_api_error(_request: Request, error: APIError) -> JSONResponse:
        return error_response(error.status_code, error.code, error.message)

    @app.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request, error: Exception
    ) -> JSONResponse:
        logger.exception(
            "Unhandled API error while processing %s %s",
            request.method,
            request.url.path,
            exc_info=error,
        )
        return error_response(
            500,
            "internal_server_error",
            "An unexpected error occurred while processing the request.",
        )
