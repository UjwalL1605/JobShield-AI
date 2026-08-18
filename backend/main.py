"""
JobShield AI — FastAPI Application Entry Point

Main application with CORS, router registration, and startup events.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from routers import analyze, report
from database.db import init_db
from services.nlp_analyzer import get_analyzer

logger = logging.getLogger("jobshield")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("🚀 Starting JobShield AI Backend...")
    init_db()

    # Pre-load ML model
    try:
        analyzer = get_analyzer()
        if analyzer.is_loaded:
            logger.info("✅ ML model ready")
        else:
            logger.warning("⚠️  ML model not loaded — run 'python ml/train_model.py' first")
    except Exception as e:
        logger.warning(f"⚠️  ML model loading failed: {e}")

    # Pre-warm EasyOCR so the first screenshot request is not slow
    # EasyOCR downloads/loads ~100MB PyTorch model — do it at startup, not on first request
    try:
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        from services.ocr_service import _get_reader

        def _load_ocr():
            reader = _get_reader()
            return reader is not None

        with ThreadPoolExecutor(max_workers=1) as ex:
            ocr_ready = await asyncio.get_running_loop().run_in_executor(ex, _load_ocr)

        if ocr_ready:
            logger.info("✅ EasyOCR model pre-loaded and ready")
        else:
            logger.warning("⚠️  EasyOCR not available — install with: pip install easyocr")
    except Exception as e:
        logger.warning(f"⚠️  EasyOCR pre-load failed: {e}")

    # Pre-warm Gemini client (validates API key early)
    try:
        from services.gemini_search_analyzer import get_genai_client
        client = get_genai_client()
        if client:
            logger.info("✅ Gemini AI client ready")
        else:
            logger.warning("⚠️  Gemini AI not configured — add GEMINI_API_KEY to backend/.env")
    except Exception as e:
        logger.warning(f"⚠️  Gemini client init failed: {e}")

    yield
    # Shutdown
    logger.info("👋 Shutting down JobShield AI Backend...")


app = FastAPI(
    title="JobShield AI",
    description="AI-powered fake job & internship scam detection platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────────────

_default_origins = "http://localhost:5173,http://localhost:3000"
ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get("CORS_ORIGINS", _default_origins).split(",") if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ─── Rate Limiting ───────────────────────────────────────────────────────────────

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
except ImportError:
    # slowapi is optional — degrade gracefully for local dev
    limiter = None
    logger.warning("slowapi not installed — rate limiting disabled. pip install slowapi")

# ─── Routes ──────────────────────────────────────────────────────────────────────

app.include_router(analyze.router)
app.include_router(report.router)


@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {
        "name": "JobShield AI",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.api_route("/api/health", methods=["GET", "HEAD"])
async def health_check():
    """Health check endpoint."""
    analyzer = get_analyzer()
    return {
        "status": "healthy",
        "ml_model_loaded": analyzer.is_loaded,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
