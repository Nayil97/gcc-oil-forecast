"""Unit tests for data loaders."""

import sys
from pathlib import Path

import pandas as pd
import pytest

# Add src to sys.path for test discovery
root_dir = Path(__file__).resolve().parents[1]
src_path = root_dir / "src"
if str(src_path) not in sys.path:
    sys.path.append(str(src_path))

from data import loaders  # type: ignore
from config import RAW_DATA_DIR  # type: ignore


# Skip test if large data file not available (e.g., in CI)
world_energy_file = Path(RAW_DATA_DIR) / "world_primary_csv.zip"
skip_world_energy = pytest.mark.skipif(
    not world_energy_file.exists(),
    reason="Large world energy data file not available in CI"
)


@skip_world_energy
def test_load_world_primary_energy() -> None:
    df = loaders.load_world_primary_energy(RAW_DATA_DIR)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_load_renewables() -> None:
    df = loaders.load_renewables(RAW_DATA_DIR)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_load_saudi_crude() -> None:
    """Test loading Saudi crude oil production data."""
    df = loaders.load_saudi_crude(RAW_DATA_DIR)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Check for date-related columns
    has_date = any(col.lower() in ['date', 'year', 'date_object'] for col in df.columns)
    assert has_date


@skip_world_energy
def test_world_energy_has_required_columns() -> None:
    """Test that world energy data has expected structure."""
    df = loaders.load_world_primary_energy(RAW_DATA_DIR)
    # Check that dataframe has some numeric columns
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    assert len(numeric_cols) > 0


def test_renewables_data_quality() -> None:
    """Test that renewables data has valid values."""
    df = loaders.load_renewables(RAW_DATA_DIR)
    # Check for no null values in key columns
    assert df.shape[0] > 0
    # Check that numeric columns don't have all NaN
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_cols:
        assert df[col].notna().sum() > 0
