"""Utility functions for file IO."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def ensure_dir(path: Path) -> None:
    """Create a directory if it does not exist."""
    path.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path, **kwargs) -> pd.DataFrame:
    """Wrapper around pandas.read_csv with path support."""
    return pd.read_csv(path, **kwargs)


def write_csv(df: pd.DataFrame, path: Path, **kwargs) -> None:
    """Write a DataFrame to CSV and ensure directory exists."""
    ensure_dir(path.parent)
    df.to_csv(path, index=False, **kwargs)
