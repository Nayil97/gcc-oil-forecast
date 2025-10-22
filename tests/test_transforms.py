"""Tests for transform utilities."""

import sys
from pathlib import Path
import pandas as pd

root_dir = Path(__file__).resolve().parents[1]
src_path = root_dir / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from data import transforms  # type: ignore


def test_add_lag_and_rolling_features() -> None:
    dates = pd.date_range(start="2020-01-01", periods=12, freq="MS")
    df = pd.DataFrame({"date": dates, "value": range(12)})
    df = transforms.add_lag_features(df, "value", lags=[1, 3])
    df = transforms.add_rolling_features(df, "value", windows=[3], stats=["mean", "std"])
    # After adding features, there should be new columns
    assert "value_lag_1" in df.columns
    assert "value_roll_mean_3" in df.columns
    assert "value_roll_std_3" in df.columns


def test_lag_features_correct_values() -> None:
    """Test that lag features have correct shifted values."""
    df = pd.DataFrame({"value": [10, 20, 30, 40, 50]})
    df = transforms.add_lag_features(df, "value", lags=[1, 2])
    # lag_1 should be previous value
    assert df.loc[1, "value_lag_1"] == 10
    assert df.loc[2, "value_lag_1"] == 20
    # lag_2 should be 2 steps back
    assert df.loc[2, "value_lag_2"] == 10
    assert df.loc[3, "value_lag_2"] == 20


def test_rolling_mean_calculation() -> None:
    """Test that rolling mean is calculated correctly."""
    df = pd.DataFrame({"value": [10, 20, 30, 40, 50]})
    df = transforms.add_rolling_features(df, "value", windows=[3], stats=["mean"])
    # Rolling mean of 3 at index 2 should be (10+20+30)/3 = 20
    assert abs(df.loc[2, "value_roll_mean_3"] - 20) < 0.01


def test_multiple_lag_windows() -> None:
    """Test that multiple lag periods are created."""
    df = pd.DataFrame({"value": range(10)})
    df = transforms.add_lag_features(df, "value", lags=[1, 3, 6])
    assert "value_lag_1" in df.columns
    assert "value_lag_3" in df.columns
    assert "value_lag_6" in df.columns


def test_multiple_rolling_stats() -> None:
    """Test that multiple rolling statistics are created."""
    df = pd.DataFrame({"value": range(10)})
    df = transforms.add_rolling_features(df, "value", windows=[3], stats=["mean", "std", "min", "max"])
    assert "value_roll_mean_3" in df.columns
    assert "value_roll_std_3" in df.columns
    assert "value_roll_min_3" in df.columns
    assert "value_roll_max_3" in df.columns
