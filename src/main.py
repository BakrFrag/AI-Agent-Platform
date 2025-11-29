from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core import settings, logger
#Routers
from src.agent import  agent_router
from src.session import session_router
from src.message import message_router
# Exception Handlers
from src.exceptions import( register_sqlalchemy_handler, register_openai_handler, register_http_handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events, ensuring database initialization.
    """
    logger.info(f"Application starting in {settings.ENV} environment. Version: {settings.APP_VERSION}")
    yield # Application continues here, ready to serve requests
    logger.info("Application shutdown initiated.")
    

app = FastAPI(
    title="AI Agent Platform API (v3 Feature-Centric, Fully Async)",
    version=settings.APP_VERSION, # Use the centralized version here
    description="Backend service for creating and interacting with AI agents. Fully Async w/ SQLAlchemy.",
    lifespan=lifespan,
    docs_url=f"/api/{settings.APP_VERSION}/docs" if settings.ENV != "production" else None,
    redoc_url=f"/api/{settings.APP_VERSION}/redoc" if settings.ENV != "production" else None
)

# Define the base API prefix using the centralized version
API_PREFIX = f"/api/{settings.APP_VERSION}"


# ROUTERS


app.include_router(agent_router, prefix=API_PREFIX)
app.include_router(session_router, prefix=API_PREFIX)
app.include_router(message_router, prefix=API_PREFIX)

# exception handlers)
app.add_exception_handler(Exception, register_sqlalchemy_handler)
app.add_exception_handler(Exception, register_openai_handler)
app.add_exception_handler(Exception, register_http_handler)


@app.get("/health/check/", tags=["System"])
async def health_check():
    """Simple endpoint to verify the service is up."""
    return {"status": "ok", "version": settings.APP_VERSION, "environment": settings.ENV}