"""Logging configuration for the project.

This module defines a helper function to configure Python's built‑in logging
module.  All scripts should call `setup_logging()` at the start to ensure
consistent formatting and output destinations.
"""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path


def setup_logging(log_dir: Path | None = None, log_filename: str = "project.log") -> None:
    """Configure logging for the entire project.

    Args:
        log_dir: Directory where the log file will be stored.  If None,
            the current working directory is used.
        log_filename: Name of the log file.
    """
    if log_dir is None:
        log_dir = Path.cwd()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / log_filename

    logging_config: dict[str, object] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "INFO",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": str(log_file),
                "maxBytes": 5 * 1024 * 1024,  # 5 MB
                "backupCount": 3,
                "level": "INFO",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
    }

    logging.config.dictConfig(logging_config)
