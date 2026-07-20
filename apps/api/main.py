from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from apps.api.routers import upload, analysis, auth
from apps.api.core.config import settings

from contextlib import asynccontextmanager
from apps.api.core.cache import init_redis, close_redis
from apps.api.core.logging import configure_logging
from asgi_correlation_id import CorrelationIdMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()

limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_GLOBAL])

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for the FairLens AI Bias Detection Platform",
    version="1.0.0",
    lifespan=lifespan,
)

Instrumentator().instrument(app).expose(app)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(CorrelationIdMiddleware)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth")
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/datasets", tags=["datasets"])
app.include_router(analysis.router, prefix=settings.API_V1_STR)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Note: TrustedHostMiddleware requires proper HOST header. In local dev, localhost is fine.
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "api"}

@app.get("/ready")
async def readiness_check():
    from apps.api.core.db import engine
    from sqlalchemy import text
    from apps.api.core.cache import redis_client
    
    # Check DB
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        return Response(status_code=503, content="Database not ready")
        
    # Check Redis
    try:
        if redis_client:
            await redis_client.ping()
        else:
            return Response(status_code=503, content="Redis not initialized")
    except Exception as e:
        return Response(status_code=503, content="Redis not ready")
    
    return {"status": "ready"}
