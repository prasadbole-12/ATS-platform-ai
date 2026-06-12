"""
app/main.py
-----------
FastAPI application entry point.
Startup: configure logging, bootstrap TF-IDF engine from existing DB data.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger("ats")
    logger.info("ATS Platform starting — env: %s", settings.ENVIRONMENT)

    # Ensure upload directory exists
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    # Bootstrap TF-IDF engine with existing data
    try:
        from app.database.session import SessionLocal
        from app.ml.tfidf_engine import bootstrap_tfidf_engine
        db = SessionLocal()
        try:
            bootstrap_tfidf_engine(db)
        finally:
            db.close()
    except Exception as exc:
        logger.warning("TF-IDF bootstrap skipped (DB not ready yet): %s", exc)

    yield

    logger.info("ATS Platform shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered ATS Candidate Ranking Platform — ML-driven resume parsing and scoring.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"], include_in_schema=False)
def health_check() -> dict:
    from app.ml.tfidf_engine import tfidf_engine
    return {
        "status":         "healthy",
        "app":            settings.APP_NAME,
        "version":        settings.APP_VERSION,
        "environment":    settings.ENVIRONMENT,
        "tfidf_fitted":   tfidf_engine.is_fitted,
        "tfidf_vocab":    tfidf_engine.vocab_size,
    }


@app.get("/", include_in_schema=False)
def root() -> dict:
    return {"message": f"Welcome to {settings.APP_NAME}", "docs": "/api/docs"}
