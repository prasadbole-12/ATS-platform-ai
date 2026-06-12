"""
app/core/logging.py
-------------------
Configures Python's standard logging for the application.
All modules should use:  logger = logging.getLogger(__name__)
This gives structured, level-filtered output for every layer.
"""

import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """Configure root logger. Called once in app startup."""

    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Silence noisy third-party loggers in production
    if not settings.DEBUG:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


logger = logging.getLogger("ats")
