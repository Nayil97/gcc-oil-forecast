"""Data transformation utilities.

This module contains generic functions for resampling time series, creating
lags and rolling statistics.  These helpers are used in the feature
engineering pipeline.
"""

from __future__ import annotations

import pandas as pd
from typing import List


def resample_to_month_start(
    df: pd.DataFrame, date_col: str, value_cols: List[str], how: str = "mean"
) -> pd.DataFrame:
    """Resample a DataFrame to monthly frequency, aggregating values.

    Args:
        df: Input DataFrame.
        date_col: Column containing dates.
        value_cols: Columns to aggregate.
        how: Aggregation method ('mean', 'sum', 'ffill', etc.).

    Returns:
        DataFrame indexed by the first day of each month with aggregated columns.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.set_index(date_col)
    
    # Special handling for forward fill
    if how == "ffill":
        # Resample to monthly and forward fill
        agg_df = df[value_cols].resample("MS").ffill()
    else:
        # Use standard aggregation methods
        agg_df = getattr(df[value_cols].resample("MS"), how)()
    
    agg_df = agg_df.reset_index()
    return agg_df


def add_lag_features(
    df: pd.DataFrame, value_col: str, lags: List[int]
) -> pd.DataFrame:
    """Add lag features to a DataFrame.

    Args:
        df: Input DataFrame sorted by date ascending.
        value_col: Column from which to create lags.
        lags: List of integer lag values (in months).

    Returns:
        DataFrame with new columns `{value_col}_lag_{lag}` for each lag.
    """
    for lag in lags:
        df[f"{value_col}_lag_{lag}"] = df[value_col].shift(lag)
    return df


def add_rolling_features(
    df: pd.DataFrame, value_col: str, windows: List[int], stats: List[str] | None = None
) -> pd.DataFrame:
    """Add rolling window statistics to a DataFrame.

    Args:
        df: Input DataFrame sorted by date ascending.
        value_col: Column for which to compute rolling features.
        windows: List of window sizes (in months).
        stats: Statistics to compute ('mean', 'std', etc.).  If None,
            defaults to ['mean', 'std'].

    Returns:
        DataFrame with new rolling feature columns.
    """
    if stats is None:
        stats = ["mean", "std"]
    for window in windows:
        for stat in stats:
            col_name = f"{value_col}_roll_{stat}_{window}"
            roll = df[value_col].rolling(window)
            if stat == "mean":
                df[col_name] = roll.mean()
            elif stat == "std":
                df[col_name] = roll.std()
            elif stat == "min":
                df[col_name] = roll.min()
            elif stat == "max":
                df[col_name] = roll.max()
            else:
                raise ValueError(f"Unsupported stat: {stat}")
    return df
