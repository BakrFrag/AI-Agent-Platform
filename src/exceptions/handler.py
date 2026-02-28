import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from openai import OpenAIError, APIError, RateLimitError, APIConnectionError, AuthenticationError
from src.core import logger  

async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler that categorizes and handles different exception types
    """
    
    # SQLAlchemy Exceptions
    if isinstance(exc, SQLAlchemyError):
        logger.error(f"Database error on {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Database connection error",
                "detail": "A database error occurred. Please try again later.",
                "type": "DatabaseError"
            }
        )
    
    # OpenAI Exceptions
    elif isinstance(exc, (OpenAIError, APIError, RateLimitError, APIConnectionError, AuthenticationError)):
        error_type = type(exc).__name__
        logger.error(f"OpenAI API error on {request.url.path}: {str(exc)}", exc_info=True)
        
        # Handle specific OpenAI errors
        if isinstance(exc, RateLimitError):
            detail = "Rate limit exceeded for OpenAI API"
            status_code = 429
        elif isinstance(exc, AuthenticationError):
            detail = "OpenAI authentication failed"
            status_code = 401
        elif isinstance(exc, APIConnectionError):
            detail = "Failed to connect to OpenAI API"
            status_code = 503
        else:
            detail = str(exc) or "OpenAI API integration error"
            status_code = 500
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": "LLM integration error",
                "detail": detail,
                "type": f"OpenAI{error_type}"
            }
        )
    
    elif isinstance(exc, HTTPException):
        logger.warning(f"HTTP exception on {request.url.path}: {exc.detail}", exc_info=True)
        raise exc
    
    elif isinstance(exc, RequestValidationError):
        logger.warning(f"Validation error on {request.url.path}: {exc.errors()}", exc_info=True)
        raise exc
    
    else:
        logger.critical(f"Unexpected error on {request.url.path}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please try again later.",
                "type": "InternalServerError"
            }
        )

def register_global_exception_handlers(app: FastAPI):
    """
    Register global exception handlers for the FastAPI application
    """
    app.add_exception_handler(Exception, global_exception_handler)
    
