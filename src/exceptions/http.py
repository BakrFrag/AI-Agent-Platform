
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from core.logger import logger

async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handles standard FastAPI HTTPExceptions (e.g., 404, 401) and uses the 
    status code defined within the exception itself (exc.status_code).
    """
    logger.warning(f"HTTPException raised for {request.url.path}: {exc.status_code} - {exc.detail}")
    
    if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.error(f"Internal Server Error details: {exc.detail}", exc_info=True) 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error occurred." 
        )
    raise exc

def register_http_handlers(app: FastAPI):
    """
    Registers the HTTPException handler to the FastAPI app.
    """
    app.add_exception_handler(HTTPException, http_exception_handler)    
    app.add_exception_handler(Exception, http_exception_handler) 