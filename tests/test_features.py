"""Tests for feature engineering."""

import sys
from pathlib import Path

import pandas as pd

root_dir = Path(__file__).resolve().parents[1]
src_path = root_dir / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from features import build_features  # type: ignore


def test_build_features() -> None:
    df = build_features.build_features()
    assert isinstance(df, pd.DataFrame)
    assert "saudi_production" in df.columns
    # Check lagged and rolling features exist
    assert any(col.endswith("_lag_1") for col in df.columns)


def test_features_no_null_target() -> None:
    """Test that target variable has no null values."""
    df = build_features.build_features()
    assert df["saudi_production"].notna().all()


def test_features_have_date_index() -> None:
    """Test that features dataframe has datetime index."""
    df = build_features.build_features()
    assert isinstance(df.index, pd.DatetimeIndex) or "date" in df.columns


def test_rolling_features_created() -> None:
    """Test that rolling window features are created."""
    df = build_features.build_features()
    rolling_cols = [col for col in df.columns if "rolling" in col.lower()]
    assert len(rolling_cols) > 0


def test_lagged_features_created() -> None:
    """Test that lagged features are created."""
    df = build_features.build_features()
    lag_cols = [col for col in df.columns if "lag" in col.lower()]
    assert len(lag_cols) > 0


def test_features_shape() -> None:
    """Test that features dataframe has reasonable shape."""
    df = build_features.build_features()
    # Should have more than 10 rows (enough historical data)
    assert len(df) > 10
    # Should have multiple features (at least target + some engineered features)
    assert len(df.columns) >= 10
