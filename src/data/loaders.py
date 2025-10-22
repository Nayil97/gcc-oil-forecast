"""Data loading utilities.

This module provides helper functions for reading the diverse raw datasets used in
the GCC oil forecasting project.  The goal is to encapsulate file format
differences and provide Pandas DataFrames with consistent schemas.
"""

from __future__ import annotations

import logging
from pathlib import Path
import zipfile
from typing import Optional

import pandas as pd


logger = logging.getLogger(__name__)


def load_zip_csv(zip_path: Path, csv_name: Optional[str] = None) -> pd.DataFrame:
    """Load a CSV file from within a ZIP archive.

    Args:
        zip_path: Path to the ZIP file.
        csv_name: Name of the CSV file within the archive.  If None, the
            first CSV encountered will be used.

    Returns:
        DataFrame containing the CSV contents.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = [name for name in zf.namelist() if name.endswith(".csv")]
        if not names:
            raise FileNotFoundError(f"No CSV files found in {zip_path}")
        target = csv_name or names[0]
        if target not in names:
            raise FileNotFoundError(f"{target} not found in {zip_path}; available: {names}")
        with zf.open(target) as f:
            df = pd.read_csv(f)
    logger.info("Loaded %s from %s", target, zip_path.name)
    return df


def load_csv(path: Path, **read_csv_kwargs) -> pd.DataFrame:
    """Load a CSV file using pandas.read_csv.

    Args:
        path: Path to the CSV file.
        **read_csv_kwargs: Additional keyword arguments passed to read_csv.

    Returns:
        DataFrame with the file contents.
    """
    logger.info("Loading CSV %s", path.name)
    return pd.read_csv(path, **read_csv_kwargs)


def load_excel(path: Path, sheet_name: int | str | None = 0, **read_excel_kwargs) -> pd.DataFrame:
    """Load an Excel file (.xls or .xlsx).

    Pandas requires either xlrd or openpyxl depending on the file format.  The
    appropriate engine is inferred automatically if the packages are installed.

    Args:
        path: Path to the Excel file.
        sheet_name: Sheet index or name to load (default first sheet).
        **read_excel_kwargs: Additional keyword arguments passed to read_excel.

    Returns:
        DataFrame with the sheet contents.
    """
    try:
        logger.info("Loading Excel %s (sheet: %s)", path.name, sheet_name)
        return pd.read_excel(path, sheet_name=sheet_name, **read_excel_kwargs)
    except ImportError as exc:
        logger.error("Unable to read %s.  Install xlrd or openpyxl to proceed.", path.name)
        raise exc


def load_world_primary_energy(raw_dir: Path) -> pd.DataFrame:
    """Load the world primary energy dataset from a ZIP archive.

    The dataset contains country‑level primary energy consumption and production.
    """
    zip_path = raw_dir / "world_primary_csv.zip"
    return load_zip_csv(zip_path)


def load_renewables(raw_dir: Path) -> pd.DataFrame:
    """Load the renewable energy installed capacity and electricity production dataset.

    The raw CSV from OWID uses semicolons as delimiters and includes multiple
    descriptor columns.  We explicitly set ``sep=';'`` to split the columns
    correctly.

    Args:
        raw_dir: Directory containing the raw datasets.

    Returns:
        DataFrame with parsed columns.
    """
    csv_path = raw_dir / "renewable-energy-installed-capacity-and-electricity-production.csv"
    # Use semicolon delimiter to correctly parse the columns
    return load_csv(csv_path, sep=";")


def load_saudi_crude(raw_dir: Path) -> pd.DataFrame:
    """Load the Saudi crude oil production dataset from a CSV file.

    The raw file uses semicolon delimiters.  We explicitly set ``sep=';'`` to
    correctly parse the columns.
    """
    csv_path = raw_dir / "saudi-crude-oil-production-from-sama-annual-statistics-2015-dec.csv"
    return load_csv(csv_path, sep=";")


def load_brent_monthly(raw_dir: Path) -> pd.DataFrame:
    """Load the monthly Brent spot price dataset from an Excel file.

    Returns a DataFrame with columns inferred from the sheet.
    The data is in the 'Data 1' sheet starting from row 3.
    """
    excel_path = raw_dir / "RBRTEm.xls"
    return load_excel(excel_path, sheet_name='Data 1', skiprows=2)


def load_brent_daily(raw_dir: Path) -> pd.DataFrame:
    """Load the daily Brent spot price dataset from an Excel file.
    """
    excel_path = raw_dir / "RBRTEd.xls"
    return load_excel(excel_path)
