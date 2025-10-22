"""Model training script.

This module trains multiple models on the processed feature matrix for different
forecast horizons.  It performs time‑aware cross‑validation, logs experiments
to MLflow and registers the best model for each horizon in the registry.

Run this module as a script:

```bash
python -m src.models.train
```

"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import mlflow
import mlflow.sklearn  # type: ignore
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import ElasticNet

try:
    import lightgbm as lgb
except ImportError:
    lgb = None  # type: ignore

try:
    from catboost import CatBoostRegressor
except ImportError:
    CatBoostRegressor = None  # type: ignore

from ..config import (
    PROCESSED_DATA_DIR,
    MLFLOW_TRACKING_URI,
    MLFLOW_EXPERIMENT_NAME,
    MODEL_REGISTRY_STAGE,
    LIGHTGBM_PARAMS,
)
from ..logging_conf import setup_logging


logger = logging.getLogger(__name__)


def load_features() -> pd.DataFrame:
    """Load the processed feature matrix from disk."""
    features_path = PROCESSED_DATA_DIR / "features.csv"
    df = pd.read_csv(features_path, parse_dates=["date"])
    return df


def time_series_cross_val(
    X: pd.DataFrame, y: pd.Series, model, n_splits: int = 5
) -> Dict[str, float]:
    """Perform time‑series cross‑validation and return evaluation metrics.

    Args:
        X: Feature matrix.
        y: Target vector.
        model: A scikit‑learn compatible regressor.
        n_splits: Number of splits for TimeSeriesSplit.

    Returns:
        Dictionary of aggregated metrics (RMSE and MAE).
    """
    tscv = TimeSeriesSplit(n_splits=n_splits)
    rmses: List[float] = []
    maes: List[float] = []
    for train_idx, val_idx in tscv.split(X):
        X_train, y_train = X.iloc[train_idx], y.iloc[train_idx]
        X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
        model.fit(X_train, y_train)
        y_pred = model.predict(X_val)
        rmses.append(mean_squared_error(y_val, y_pred, squared=False))
        maes.append(mean_absolute_error(y_val, y_pred))
    return {"rmse": float(np.mean(rmses)), "mae": float(np.mean(maes))}


def train_and_log_model(
    X: pd.DataFrame,
    y: pd.Series,
    horizon: int,
    model_name: str,
    params: Dict[str, object],
    model_type: str,
) -> Dict[str, object]:
    """Train a model, perform cross‑validation and log the run to MLflow.

    Args:
        X: Feature matrix.
        y: Target vector.
        horizon: Forecast horizon in months.
        model_name: Name of the model class.
        params: Hyperparameters for the model.
        model_type: Identifier used in MLflow model name.

    Returns:
        Dictionary with metrics and run information.
    """
    if model_type == "lightgbm":
        if lgb is None:
            raise ImportError("LightGBM is not installed")
        model = lgb.LGBMRegressor(**params)
    elif model_type == "catboost":
        if CatBoostRegressor is None:
            raise ImportError("CatBoost is not installed")
        model = CatBoostRegressor(**params, verbose=False)
    elif model_type == "elasticnet":
        model = ElasticNet(**params)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

    with mlflow.start_run(run_name=f"h{horizon}_{model_type}"):
        # Log hyperparameters
        mlflow.log_params(params)
        # Cross‑validation
        cv_metrics = time_series_cross_val(X, y, model)
        mlflow.log_metric("rmse", cv_metrics["rmse"])
        mlflow.log_metric("mae", cv_metrics["mae"])
        # Fit on full data
        model.fit(X, y)
        # Log model
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=f"gcc_oil_forecast_h{horizon}_{model_type}",
        )
        run_id = mlflow.active_run().info.run_id
    return {"metrics": cv_metrics, "run_id": run_id}


def train_all_horizons() -> None:
    """Train models for forecast horizons 1 to 6 and register the best ones.
    """
    setup_logging(Path("logs"))
    logger.info("Starting training for all horizons")
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    df = load_features()

    target = "saudi_production"
    feature_cols = [c for c in df.columns if c not in {"date", target} and not c.startswith(target)]

    results = []
    # Define simple hyperparameters for demonstration
    lightgbm_params = LIGHTGBM_PARAMS
    catboost_params = {"depth": 6, "learning_rate": 0.05, "iterations": 500}
    elasticnet_params = {"alpha": 0.1, "l1_ratio": 0.5}

    for horizon in [1, 2, 3, 4, 5, 6]:
        logger.info("Training models for horizon %d", horizon)
        # Shift target forward by horizon months
        df_h = df.copy()
        df_h[f"target_h{horizon}"] = df_h[target].shift(-horizon)
        df_h = df_h.dropna(subset=[f"target_h{horizon}"])
        X = df_h[feature_cols]
        y = df_h[f"target_h{horizon}"]

        # Train each model type and collect metrics
        metrics_dict = {}
        for model_type, params in [
            ("lightgbm", lightgbm_params),
            ("catboost", catboost_params),
            ("elasticnet", elasticnet_params),
        ]:
            res = train_and_log_model(
                X=X,
                y=y,
                horizon=horizon,
                model_name="gcc_oil_forecast",
                params=params,
                model_type=model_type,
            )
            metrics_dict[model_type] = res
        # Determine best model by lowest RMSE
        best_model_type = min(metrics_dict, key=lambda m: metrics_dict[m]["metrics"]["rmse"])
        best_run_id = metrics_dict[best_model_type]["run_id"]
        logger.info(
            "Horizon %d best model: %s (RMSE %.4f)",
            horizon,
            best_model_type,
            metrics_dict[best_model_type]["metrics"]["rmse"],
        )
        # Transition best model to desired stage
        model_uri = f"runs:/{best_run_id}/model"
        registered_name = f"gcc_oil_forecast_h{horizon}_{best_model_type}"
        # register model version and transition to stage
        mv = mlflow.register_model(model_uri, registered_name)
        client = mlflow.tracking.MlflowClient()
        client.transition_model_version_stage(
            name=registered_name,
            version=mv.version,
            stage=MODEL_REGISTRY_STAGE,
            archive_existing_versions=True,
        )
        results.append({"horizon": horizon, "model_type": best_model_type, "run_id": best_run_id})

    logger.info("Training complete.  Results: %s", results)


if __name__ == "__main__":
    train_all_horizons()
