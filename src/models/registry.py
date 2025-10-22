"""MLflow model registry helpers.

This module provides convenience functions for querying the MLflow model
registry.  It is used by the API and Streamlit applications to discover
available models and their metadata.
"""

from __future__ import annotations

import logging
from typing import Optional, List, Dict

import mlflow

from ..config import MLFLOW_TRACKING_URI, MODEL_REGISTRY_STAGE


logger = logging.getLogger(__name__)


def list_models(prefix: Optional[str] = None, stage: str = MODEL_REGISTRY_STAGE) -> List[str]:
    """List registered model names filtered by prefix and stage.

    Args:
        prefix: Optional prefix that model names must start with.
        stage: Desired stage (e.g., `Production`, `Staging`).

    Returns:
        List of model names.
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = mlflow.tracking.MlflowClient()
    names = []
    for rm in client.list_registered_models():
        name = rm.name
        if prefix and not name.startswith(prefix):
            continue
        for mv in rm.latest_versions:
            if mv.current_stage == stage:
                names.append(name)
                break
    return names


def get_model_metadata(name: str, stage: str = MODEL_REGISTRY_STAGE) -> Dict[str, object]:
    """Retrieve basic metadata for a registered model.

    Args:
        name: Name of the registered model.
        stage: Stage to fetch (default uses global stage).

    Returns:
        Dictionary containing run ID, version and tags.
    """
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = mlflow.tracking.MlflowClient()
    for mv in client.get_latest_versions(name, stages=[stage]):
        return {
            "name": name,
            "run_id": mv.run_id,
            "version": mv.version,
            "stage": mv.current_stage,
            "source": mv.source,
        }
    raise ValueError(f"No model named {name} in stage {stage}")
