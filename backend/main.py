"""
JobShield AI — FastAPI Application Entry Point

Main application with CORS, router registration, and startup events.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from routers import analyze, report
from database.db import init_db
from services.nlp_analyzer import get_analyzer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    print("🚀 Starting JobShield AI Backend...")
    init_db()
    # Pre-load ML model
    try:
        analyzer = get_analyzer()
        if analyzer._loaded:
            print("✅ ML model ready")
        else:
            print("⚠️  ML model not loaded — run 'python ml/train_model.py' first")
    except Exception as e:
        print(f"⚠️  ML model loading failed: {e}")

    yield
    # Shutdown
    print("👋 Shutting down JobShield AI Backend...")


app = FastAPI(
    title="JobShield AI",
    description="AI-powered fake job & internship scam detection platform",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

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
        "ml_model_loaded": analyzer._loaded,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
