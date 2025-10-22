"""Model inference utilities.

This module provides helper functions and classes to load models from the
MLflow registry and generate forecasts for arbitrary future dates.  It
encapsulates the logic required to compute lags and rolling statistics for
exogenous scenarios and aligns input data with the feature schema used during
training.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import mlflow
import pandas as pd

from ..config import (
    MLFLOW_TRACKING_URI,
    MODEL_REGISTRY_STAGE,
    PROCESSED_DATA_DIR,
)
from ..data import transforms


logger = logging.getLogger(__name__)


class Forecaster:
    """A wrapper class for loading and using a model from the MLflow registry."""

    def __init__(self, horizon: int) -> None:
        self.horizon = horizon
        self.model = None
        self.feature_columns: Optional[List[str]] = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the latest model for this horizon from MLflow."""
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        client = mlflow.tracking.MlflowClient()
        # Models are registered with names like gcc_oil_forecast_h{horizon}_<model_type>
        prefix = f"gcc_oil_forecast_h{self.horizon}_"
        # Fetch all model versions with the given prefix and stage
        for registered_model in client.list_registered_models():
            name = registered_model.name
            if not name.startswith(prefix):
                continue
            # Find version in desired stage
            for mv in registered_model.latest_versions:
                if mv.current_stage == MODEL_REGISTRY_STAGE:
                    logger.info(
                        "Loading model %s version %s from stage %s",
                        name,
                        mv.version,
                        MODEL_REGISTRY_STAGE,
                    )
                    self.model = mlflow.pyfunc.load_model(model_uri=f"models:/{name}/{MODEL_REGISTRY_STAGE}")
                    # Retrieve feature columns from model signature if available
                    try:
                        sig = mlflow.models.Model.load(f"models:/{name}/{MODEL_REGISTRY_STAGE}").signature
                        if sig is not None:
                            self.feature_columns = [col.name for col in sig.inputs]
                    except Exception:
                        self.feature_columns = None
                    return
        raise RuntimeError(f"No model found for horizon {self.horizon} in stage {MODEL_REGISTRY_STAGE}")

    def _prepare_inputs(
        self, dates: List[pd.Timestamp], scenario: Dict[str, List[float]]
    ) -> pd.DataFrame:
        """Prepare a feature matrix for the requested prediction dates.

        This implementation creates features by taking the last known processed
        record and applying the scenario values.  It then recomputes lags and
        rolling statistics using historical data.  For simplicity, prediction
        intervals are not computed here.
        """
        # Load processed features for baseline
        base_df = pd.read_csv(PROCESSED_DATA_DIR / "features.csv", parse_dates=["date"])
        base_df.sort_values("date", inplace=True)
        last_row = base_df.iloc[-1]
        rows = []
        for idx, date in enumerate(dates):
            row = last_row.copy()
            row["date"] = pd.to_datetime(date)
            # Override scenario values if provided
            for var, values in scenario.items():
                if idx < len(values) and var in row.index:
                    row[var] = values[idx]
            rows.append(row)
        df_pred = pd.DataFrame(rows)
        # Combine with base for lag computations
        combined = pd.concat([base_df, df_pred], ignore_index=True)
        combined.sort_values("date", inplace=True)
        # Recompute lags and rolling features for each variable present in training
        target_col = "saudi_production"
        feature_cols = [c for c in base_df.columns if c not in {"date", target_col}]
        for col in [target_col] + feature_cols:
            combined = transforms.add_lag_features(combined, col, lags=[1, 2, 3, 6, 12])
            combined = transforms.add_rolling_features(combined, col, windows=[3, 6, 12])
        # Drop rows that don't have full lags (the original training data)
        combined.dropna(inplace=True)
        # Extract only the prediction rows
        pred_df = combined[combined["date"].isin(dates)]
        # Keep only feature columns used in training
        if self.feature_columns is not None:
            X = pred_df[self.feature_columns]
        else:
            # Fallback: drop date and target columns
            drop_cols = ["date", target_col] + [c for c in combined.columns if c.startswith(target_col)]
            X = pred_df.drop(columns=drop_cols)
        return X

    def predict(
        self, dates: List[str], scenario: Optional[Dict[str, List[float]]] = None
    ) -> List[float]:
        """Generate forecasts for the given dates.

        Args:
            dates: List of ISO 8601 date strings (YYYY‑MM‑DD) representing the
                first day of each month to predict.
            scenario: Optional dictionary of scenario values keyed by feature
                name.  Each value should be a list aligned with the dates list.

        Returns:
            List of predicted production values.
        """
        if scenario is None:
            scenario = {}
        dates_parsed = [pd.to_datetime(d) for d in dates]
        X_pred = self._prepare_inputs(dates_parsed, scenario)
        preds = self.model.predict(X_pred)
        return preds.tolist()
