"""Backtesting utilities for time‑series forecasts.

This module provides functions to evaluate models using rolling origin
backtesting, capturing how errors evolve across different forecast horizons.
"""

from __future__ import annotations

from typing import Callable, Dict, List

import numpy as np
import pandas as pd

from .metrics import rmse, mae, smape


def rolling_origin_backtest(
    df: pd.DataFrame,
    target_col: str,
    feature_cols: List[str],
    horizon: int,
    train_size: int,
    step: int,
    model_factory: Callable[[], object],
) -> Dict[str, float]:
    """Perform rolling origin backtesting.

    Args:
        df: Feature DataFrame sorted by date.
        target_col: Name of the target column.
        feature_cols: List of feature columns.
        horizon: Number of steps ahead to forecast.
        train_size: Number of observations to use for the initial training window.
        step: Step size to move the origin forward.
        model_factory: Callable that returns a new, untrained model instance.

    Returns:
        Dictionary of aggregated metrics across all folds.
    """
    rmses: List[float] = []
    maes: List[float] = []
    smapes: List[float] = []
    for start in range(0, len(df) - train_size - horizon + 1, step):
        train_end = start + train_size
        test_end = train_end + horizon
        train_df = df.iloc[start:train_end]
        test_df = df.iloc[train_end:test_end]
        X_train, y_train = train_df[feature_cols], train_df[target_col]
        X_test, y_test = test_df[feature_cols], test_df[target_col]
        model = model_factory()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        y_true = y_test.values
        rmses.append(rmse(y_true, preds))
        maes.append(mae(y_true, preds))
        smapes.append(smape(y_true, preds))
    return {
        "rmse": float(np.mean(rmses)),
        "mae": float(np.mean(maes)),
        "smape": float(np.mean(smapes)),
    }
