"""
Error handling middleware for FastAPI.
"""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import traceback

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to handle errors globally."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            # Re-raise HTTP exceptions to let FastAPI handle them
            raise exc
        except Exception as exc:
            # Log the error
            logger.error(f"Unhandled error in {request.method} {request.url}: {exc}")
            logger.error(traceback.format_exc())

            # Return a generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "path": str(request.url.path),
                },
            )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
        },
    )


async def validation_exception_handler(request: Request, exc):
    """Custom validation exception handler."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors() if hasattr(exc, "errors") else str(exc),
            "path": str(request.url.path),
        },
    )
