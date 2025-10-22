"""Project configuration constants.

This module centralises configuration values so they can be easily reused and overridden.
Values are read from environment variables with sensible defaults for development.
"""

from __future__ import annotations

import os
from pathlib import Path


# Base directory of the project (assumes this file lives in src/)
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# MLflow configuration
MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
MLFLOW_EXPERIMENT_NAME: str = os.getenv("MLFLOW_EXPERIMENT_NAME", "gcc_oil_forecast")
MODEL_REGISTRY_STAGE: str = os.getenv("MODEL_REGISTRY_STAGE", "Production")

# API ports (used by docker-compose and scripts)
PORT_API: int = int(os.getenv("PORT_API", "8000"))
PORT_APP: int = int(os.getenv("PORT_APP", "8501"))

# Default modelling hyperparameters (can be overridden via CLI or environment)
LIGHTGBM_PARAMS = {
    "n_estimators": int(os.getenv("LGBM_N_ESTIMATORS", "500")),
    "learning_rate": float(os.getenv("LGBM_LEARNING_RATE", "0.05")),
    "max_depth": int(os.getenv("LGBM_MAX_DEPTH", "6")),
    "num_leaves": int(os.getenv("LGBM_NUM_LEAVES", "31")),
    "subsample": float(os.getenv("LGBM_SUBSAMPLE", "0.8")),
    "colsample_bytree": float(os.getenv("LGBM_COLSAMPLE_BYTREE", "0.8")),
    "min_child_samples": int(os.getenv("LGBM_MIN_CHILD_SAMPLES", "20")),
}
