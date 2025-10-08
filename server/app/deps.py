"""
Dependency injection and middleware for FastAPI
"""

import time
import uuid
from typing import Optional
from fastapi import HTTPException, Request, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import structlog

from .config import settings

logger = structlog.get_logger()

# Security scheme for API key authentication
security = HTTPBearer(auto_error=False)


async def get_request_id() -> str:
    """Generate unique request ID for tracing"""
    return str(uuid.uuid4())


async def verify_api_key(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    x_api_key: Optional[str] = Header(None)
) -> Optional[str]:
    """
    Verify API key from Authorization header or x-api-key header
    Returns the API key if valid, None if not required
    """
    if not settings.api_key_required:
        return None
    
    # Try x-api-key header first
    if x_api_key:
        return x_api_key
    
    # Try Authorization header
    if credentials and credentials.scheme.lower() == "bearer":
        return credentials.credentials
    
    # No valid API key found
    raise HTTPException(
        status_code=401,
        detail="API key required. Provide via 'x-api-key' header or 'Authorization: Bearer <key>'"
    )


async def log_request(request: Request, call_next):
    """Log incoming requests with timing"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        request_id=request_id,
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        "Request completed",
        request_id=request_id,
        status_code=response.status_code,
        process_time=process_time
    )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


async def handle_rate_limit_exceeded(request: Request, call_next):
    """Handle rate limiting with proper error responses"""
    try:
        response = await call_next(request)
        return response
    except HTTPException as e:
        if e.status_code == 429:
            # Rate limit exceeded
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": 60,  # Default retry after 1 minute
                    "limit": settings.rate_limit_requests,
                    "window": settings.rate_limit_window
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(settings.rate_limit_requests),
                    "X-RateLimit-Window": str(settings.rate_limit_window)
                }
            )
        raise


async def handle_cors_preflight(request: Request, call_next):
    """Handle CORS preflight requests"""
    if request.method == "OPTIONS":
        return JSONResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, x-api-key",
                "Access-Control-Max-Age": "86400"
            }
        )
    
    response = await call_next(request)
    return response


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    # Check for forwarded headers first
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


def setup_cors_headers(response: JSONResponse, request: Request) -> JSONResponse:
    """Add CORS headers to response"""
    origin = request.headers.get("Origin", "*")
    
    # Check if origin is allowed
    if settings.allowed_origins and "*" not in settings.allowed_origins:
        if origin not in settings.allowed_origins:
            origin = settings.allowed_origins[0] if settings.allowed_origins else "*"
    
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, x-api-key"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response
