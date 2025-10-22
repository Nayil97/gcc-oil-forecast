"""Tests for model training utilities."""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parents[1]
src_path = root_dir / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from models import train  # type: ignore
import pandas as pd


def test_time_series_cross_val() -> None:
    # Create dummy dataset
    X = pd.DataFrame({"x": range(10)})
    y = pd.Series(range(10))
    model = __import__("sklearn.linear_model").linear_model.LinearRegression()
    metrics = train.time_series_cross_val(X, y, model, n_splits=2)
    assert "rmse" in metrics
    assert "mae" in metrics


def test_time_series_cross_val_returns_numeric() -> None:
    """Test that cross-validation returns numeric metrics."""
    X = pd.DataFrame({"x": range(20)})
    y = pd.Series(range(20))
    model = __import__("sklearn.linear_model").linear_model.LinearRegression()
    metrics = train.time_series_cross_val(X, y, model, n_splits=3)
    assert isinstance(metrics["rmse"], (int, float))
    assert isinstance(metrics["mae"], (int, float))
    assert metrics["rmse"] >= 0
    assert metrics["mae"] >= 0


def test_time_series_cross_val_min_splits() -> None:
    """Test that cross-validation requires minimum data for splits."""
    X = pd.DataFrame({"x": range(10)})
    y = pd.Series(range(10))
    model = __import__("sklearn.linear_model").linear_model.LinearRegression()
    # Should work with 2 splits on 10 samples
    metrics = train.time_series_cross_val(X, y, model, n_splits=2)
    assert metrics is not None


def test_cross_val_with_different_models() -> None:
    """Test cross-validation works with different model types."""
    from sklearn.tree import DecisionTreeRegressor
    X = pd.DataFrame({"x1": range(20), "x2": range(20, 40)})
    y = pd.Series(range(20))
    
    # Test with Decision Tree
    model = DecisionTreeRegressor(random_state=42)
    metrics = train.time_series_cross_val(X, y, model, n_splits=2)
    assert "rmse" in metrics
    assert "mae" in metrics
