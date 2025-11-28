from fastapi import Request, status
from fastapi.responses import JSONResponse
from openai import (
    APIError,
    APIConnectionError,
    RateLimitError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    PermissionDeniedError,
    UnprocessableEntityError,
    InternalServerError,
    APITimeoutError
)
from src.core import logger


async def openai_exception_handler(request: Request, exc: Exception):
    """
    Global handler for OpenAI client exceptions
    Handles APIError, APIConnectionError, RateLimitError, AuthenticationError, etc.
    """
    logger.error(f"OpenAI error on {request.url.path}: {str(exc)}", exc_info=True)

    if isinstance(exc, AuthenticationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "OpenAI authentication failed",
                "detail": "Invalid API key or authentication credentials",
                "type": "AuthenticationError"
            }
        )
    
    # Handle RateLimitError
    elif isinstance(exc, RateLimitError):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "OpenAI rate limit exceeded",
                "detail": "Too many requests. Please try again later",
                "type": "RateLimitError"
            }
        )
    
    # Handle APIConnectionError
    elif isinstance(exc, APIConnectionError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "OpenAI connection error",
                "detail": "Could not connect to OpenAI API",
                "type": "APIConnectionError"
            }
        )
    
    # Handle APITimeoutError
    elif isinstance(exc, APITimeoutError):
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "error": "OpenAI request timeout",
                "detail": "The request to OpenAI API timed out",
                "type": "APITimeoutError"
            }
        )
    
    # Handle BadRequestError
    elif isinstance(exc, BadRequestError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid OpenAI request",
                "detail": "The request to OpenAI API was invalid",
                "type": "BadRequestError",
                "message": str(exc)
            }
        )
    
    # Handle NotFoundError
    elif isinstance(exc, NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "OpenAI resource not found",
                "detail": "The requested OpenAI resource was not found",
                "type": "NotFoundError"
            }
        )
    
    # Handle PermissionDeniedError
    elif isinstance(exc, PermissionDeniedError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "error": "OpenAI permission denied",
                "detail": "Insufficient permissions for this OpenAI operation",
                "type": "PermissionDeniedError"
            }
        )
    
    # Handle UnprocessableEntityError
    elif isinstance(exc, UnprocessableEntityError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "OpenAI unprocessable entity",
                "detail": "The request was well-formed but contains semantic errors",
                "type": "UnprocessableEntityError",
                "message": str(exc)
            }
        )
    
    # Handle InternalServerError
    elif isinstance(exc, InternalServerError):
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "error": "OpenAI internal server error",
                "detail": "OpenAI API is experiencing issues",
                "type": "InternalServerError"
            }
        )
    
    # Handle generic APIError
    elif isinstance(exc, APIError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "OpenAI API error",
                "detail": "An error occurred with the OpenAI API",
                "type": "APIError",
                "message": str(exc)
            }
        )
    
    # Catch-all for other OpenAI exceptions
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "OpenAI error",
            "detail": "An unexpected error occurred with OpenAI",
            "type": "OpenAIError",
            "message": str(exc)
        }
    )
