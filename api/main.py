"""
CityPulse REST API - Main FastAPI Application

This module provides the main FastAPI application for the CityPulse platform,
including all REST endpoints for Events, Users, Feedback, and Analytics.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

# Add parent directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from auth.firebase_auth import FirebaseAuthMiddleware
from routers import analytics, events, feedback, users
from utils.validation import ValidationError

from shared_exceptions import ErrorResponse, ValidationException

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting CityPulse API server...")

    # Initialize services, database connections, etc.
    # This is where we could add health checks, cache warming, etc.

    yield

    # Shutdown
    logger.info("Shutting down CityPulse API server...")


# Create FastAPI application
app = FastAPI(
    title="CityPulse API",
    description="The official REST API for the CityPulse platform, providing services for urban issue reporting, data management, and user engagement.",
    version="1.0.0",
    contact={
        "name": "CityPulse Development Team",
        "email": "dev@citypulse.example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "https://api.citypulse.example.com/v1",
            "description": "Production Server",
        },
        {
            "url": "https://staging-api.citypulse.example.com/v1",
            "description": "Staging Server",
        },
        {"url": "http://localhost:8000/v1", "description": "Development Server"},
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, allowed_hosts=["*"]  # Configure appropriately for production
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "https://citypulse.example.com",  # Production frontend
        "https://staging.citypulse.example.com",  # Staging frontend
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add Firebase authentication middleware
app.add_middleware(FirebaseAuthMiddleware)


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="HTTP_ERROR",
            message=exc.detail,
            status_code=exc.status_code,
            path=str(request.url.path),
        ).model_dump(),
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle legacy validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=422,
            path=str(request.url.path),
            details=getattr(exc, "errors", {}),
        ).model_dump(),
    )


@app.exception_handler(ValidationException)
async def validation_exception_handler(
    request: Request, exc: ValidationException
) -> JSONResponse:
    """Handle shared validation exceptions."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error=exc.error_code.value,
            message=exc.message,
            status_code=422,
            path=str(request.url.path),
            details=exc.details,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            status_code=500,
            path=str(request.url.path),
        ).model_dump(),
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "service": "citypulse-api",
        "version": "1.0.0",
        "timestamp": "2025-01-07T00:00:00Z",
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint with API information."""
    return {
        "message": "Welcome to CityPulse API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers with v1 prefix
app.include_router(events.router, prefix="/v1/events", tags=["Events"])
app.include_router(users.router, prefix="/v1/users", tags=["Users"])
app.include_router(feedback.router, prefix="/v1/feedback", tags=["Feedback"])
app.include_router(analytics.router, prefix="/v1/analytics", tags=["Analytics"])


def custom_openapi():
    """Generate custom OpenAPI schema with additional security definitions."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "FirebaseAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Firebase Authentication JWT token",
        },
        "ApiKey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API key for public endpoints",
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    # Development server
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
