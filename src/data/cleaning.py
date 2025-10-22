"""Data cleaning functions.

This module contains helper functions to clean and standardise raw datasets.  The
goal is to harmonise column names, parse dates and handle missing values in a
consistent way.  Many operations here are specific to the OWID energy tables
and the SAMA statistics used in this project.
"""

from __future__ import annotations

import logging
from typing import Iterable

import pandas as pd

logger = logging.getLogger(__name__)


def _standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Make column names lowercase and replace spaces with underscores.

    Args:
        df: Input DataFrame.
    Returns:
        DataFrame with normalised column names.
    """
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_").replace("/", "_") for c in df.columns]
    return df


def clean_world_primary_energy(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the world primary energy dataset.

    This includes renaming columns, parsing the year to a datetime and filtering
    to the GCC countries of interest.
    """
    df = _standardise_columns(df)
    # Parse a date column if present.  Some OWID tables use 'year', others use 'time_period'.
    if "year" in df.columns:
        df["date"] = pd.to_datetime(df["year"].astype(str) + "-01-01")
    elif "time_period" in df.columns:
        # time_period may be year-month format (YYYY-MM).  Coerce to datetime.
        df["date"] = pd.to_datetime(df["time_period"], errors="coerce")
    # Restrict to GCC countries if present (ref_area or country codes)
    gcc_countries = ["saudi arabia", "united arab emirates", "kuwait", "qatar", "oman", "bahrain"]
    if "country" in df.columns:
        df = df[df["country"].str.lower().isin(gcc_countries)]
    elif "ref_area" in df.columns:
        # Use ISO alpha-2 codes for GCC members
        gcc_codes = {"SA", "AE", "KW", "QA", "OM", "BH"}
        df = df[df["ref_area"].str.upper().isin(gcc_codes)]
    # Convert obs_value column to numeric if present
    for col in ["obs_value", "value"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def clean_renewables(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the renewable energy dataset.

    Parses year to datetime and standardises column names.
    """
    df = _standardise_columns(df)
    # Parse a date column if present.  Accept 'year' or 'time_period'.
    if "year" in df.columns:
        df["date"] = pd.to_datetime(df["year"].astype(str) + "-01-01")
    elif "time_period" in df.columns:
        # If time_period is numeric (year), convert to string and append '-01-01' for annual frequency
        df["date"] = pd.to_datetime(df["time_period"].astype(str) + "-01-01", errors="coerce")
    return df


def clean_saudi_crude(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the Saudi crude oil production dataset.

    The raw file contains annual production values.  We rename columns and parse
    the year to a datetime index.  Missing values are forward filled.
    """
    df = _standardise_columns(df)
    # Identify the year and production columns heuristically
    year_cols = [c for c in df.columns if "year" in c]
    prod_cols = [c for c in df.columns if "production" in c or "output" in c]
    if year_cols:
        df["date"] = pd.to_datetime(df[year_cols[0]].astype(str) + "-01-01")
    # Forward fill missing production values
    for col in prod_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].ffill()
    return df


def parse_date_column(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Ensure a column is parsed as pandas datetime.

    Args:
        df: Input DataFrame.
        date_col: Name of the date column.

    Returns:
        DataFrame with parsed datetime column.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    return df


def filter_columns(df: pd.DataFrame, cols: Iterable[str]) -> pd.DataFrame:
    """Filter DataFrame to contain only specified columns if they exist.

    Args:
        df: Input DataFrame.
        cols: Columns to keep.

    Returns:
        Filtered DataFrame.
    """
    existing = [c for c in cols if c in df.columns]
    return df[existing]
