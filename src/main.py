"""
MCQ Quiz Platform - FastAPI Application
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from .config.settings import get_settings
from .config.database import init_beanie
from .api.endpoints import quiz, answer
from .api.schemas import HealthResponse

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Get application settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting MCQ Quiz Platform...")
    await init_beanie()
    logger.info("MongoDB initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MCQ Quiz Platform...")


# Create FastAPI application
app = FastAPI(
    title="MCQ Quiz Platform",
    description="A scalable platform for managing multiple-choice question quizzes",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=settings.allowed_methods_list,
    allow_headers=settings.allowed_headers_list,
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    logger.error(
        "Unhandled exception occurred",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "success": False
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health Check"])
async def health_check():
    """Health check endpoint."""
    from datetime import datetime
    
    return HealthResponse(
        status="healthy",
        service="MCQ Quiz Platform",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )


# Include API routers
app.include_router(quiz.router)
app.include_router(answer.router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to MCQ Quiz Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Simple test endpoint for CORS
@app.get("/test-cors", tags=["Test"])
async def test_cors():
    """Simple endpoint to test CORS."""
    return {"status": "cors working", "message": "If you can see this, CORS is configured correctly"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
