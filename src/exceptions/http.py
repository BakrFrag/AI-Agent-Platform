
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from src.core import logger

async def http_exception_handler(request: Request, exc: HTTPException | Exception):
    """
    Handles standard FastAPI HTTPExceptions (e.g., 404, 401) and uses the 
    status code defined within the exception itself (exc.status_code).
    """
    exc_code = hasattr(exc, "status_code")
    logger.warning(f"HTTPException raised for {request.url.path}: - {str(exc)}")
    if not exc_code or exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.error(f"Internal Server Error details: {str(exc)}", exc_info=True) 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred." 
        )
    logger.error(f"exc code {exc.status_code}")
    raise exc

def register_http_handler(app: FastAPI):
    """
    Registers all exception handlers to the FastAPI app.
    """
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, http_exception_handler)