from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InvalidRequestError,
    OperationalError,
    ProgrammingError,
    SQLAlchemyError
)
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Global handler for all SQLAlchemy exceptions including SQLite-specific errors"""
    
    # Log the full error for debugging
    logger.error(f"SQLAlchemy error on {request.url.path}: {str(exc)}", exc_info=True)
    
    # Extract the original SQLite error if available
    sqlite_error = None
    if hasattr(exc, 'orig') and isinstance(exc.orig, sqlite3.Error):
        sqlite_error = exc.orig
    
    # Handle IntegrityError (UNIQUE, FOREIGN KEY, CHECK, NOT NULL)
    if isinstance(exc, IntegrityError):
        error_msg = str(sqlite_error) if sqlite_error else str(exc)
        
        # Parse specific SQLite integrity constraint violations
        if "UNIQUE constraint failed" in error_msg:
            field = error_msg.split("UNIQUE constraint failed:")[-1].strip()
            detail = f"Duplicate value for {field}"
        elif "FOREIGN KEY constraint failed" in error_msg:
            detail = "Referenced record does not exist or is being referenced"
        elif "NOT NULL constraint failed" in error_msg:
            field = error_msg.split("NOT NULL constraint failed:")[-1].strip()
            detail = f"Required field {field} cannot be empty"
        elif "CHECK constraint failed" in error_msg:
            detail = "Value does not meet check constraint requirements"
        else:
            detail = "The operation violates database constraints"
        
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "Database integrity error",
                "detail": detail,
                "type": "IntegrityError"
            }
        )
    
    # Handle DataError (data type or value errors)
    elif isinstance(exc, DataError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Invalid data",
                "detail": "The data provided is invalid or incompatible with the database schema",
                "type": "DataError"
            }
        )
    
    # Handle OperationalError (connection, locked database, disk I/O)
    elif isinstance(exc, OperationalError):
        error_msg = str(sqlite_error) if sqlite_error else str(exc)
        
        if "database is locked" in error_msg.lower():
            detail = "Database is currently locked, please try again"
        elif "unable to open database" in error_msg.lower():
            detail = "Could not open database file"
        elif "disk i/o error" in error_msg.lower():
            detail = "Database disk I/O error occurred"
        else:
            detail = "Database operation failed"
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "Database operational error",
                "detail": detail,
                "type": "OperationalError"
            }
        )
    
    # Handle ProgrammingError (SQL syntax errors, table not found)
    elif isinstance(exc, ProgrammingError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database programming error",
                "detail": "Invalid database operation",
                "type": "ProgrammingError"
            }
        )
    
    # Handle InvalidRequestError (invalid ORM usage)
    elif isinstance(exc, InvalidRequestError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid database request",
                "detail": "The database request is invalid or malformed",
                "type": "InvalidRequestError"
            }
        )
    
    # Handle DatabaseError (generic database error)
    elif isinstance(exc, DatabaseError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database error",
                "detail": "A database error occurred",
                "type": "DatabaseError"
            }
        )
    
    # Catch-all for other SQLAlchemy errors
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error",
            "detail": "An unexpected database error occurred",
            "type": "SQLAlchemyError"
        }
    )


async def sqlite_exception_handler(request: Request, exc: sqlite3.Error):
    """Handler for raw sqlite3 exceptions that might escape SQLAlchemy"""
    logger.error(f"SQLite error on {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error",
            "detail": "A SQLite database error occurred",
            "type": "SQLite3Error"
        }
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app
    
    Usage:
        from exceptions import register_exception_handlers
        register_exception_handlers(app)
    """
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(sqlite3.Error, sqlite_exception_handler)
