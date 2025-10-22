"""Feature engineering pipeline.

This script combines the cleaned datasets and constructs a feature matrix suitable
for model training.  It creates lagged and rolling features for key variables
and outputs a processed CSV for downstream modelling.

You can run this module as a script:

```bash
python -m src.features.build_features
```

This will read raw data from the directory specified in `config.RAW_DATA_DIR`,
apply transformations and save the resulting feature matrix to
`config.PROCESSED_DATA_DIR / "features.csv"`.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from ..data import loaders, cleaning, transforms
from ..logging_conf import setup_logging


logger = logging.getLogger(__name__)


def aggregate_world_energy(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate world primary energy consumption.

    The input DataFrame is expected to contain a `date` column and numeric energy
    columns.  We sum all numeric columns to produce a single world energy
    indicator.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    agg = (
        df.groupby("date")[numeric_cols]
        .sum()
        .rename(columns=lambda c: f"world_{c}")
        .reset_index()
    )
    return agg


def aggregate_renewables(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate renewable capacity and generation across GCC countries.

    The input DataFrame should contain `date` and numeric columns such as
    `renewables_capacity` and `renewables_electricity_production`.  We sum
    across the GCC countries for each date.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    agg = (
        df.groupby("date")[numeric_cols]
        .sum()
        .rename(columns=lambda c: f"renewables_{c}")
        .reset_index()
    )
    return agg


def prepare_saudi_production(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the Saudi production DataFrame.

    Renames the production column to `saudi_production` and selects only
    relevant columns. Filters to 'Total' production values only.
    """
    df = df.copy()
    
    # Filter to only "Total" production indicator (not "Percentage Change")
    # Check for various possible column names
    indicator_col = None
    for col in ['production_indicator', 'Production Indicator', 'production indicator']:
        if col in df.columns:
            indicator_col = col
            break
    
    if indicator_col and df[indicator_col].notna().any():
        # Convert to string and filter for 'Total'
        df = df[df[indicator_col].astype(str).str.lower().str.contains('total', na=False)]
    
    # Look for 'value' column first (the actual production values)
    if 'value' in df.columns:
        prod_col = 'value'
    else:
        # Fallback: Find the first numeric column as production (excluding 'year')
        numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns.tolist() 
                       if c not in {'year', 'production_indicator'}]
        if numeric_cols:
            prod_col = numeric_cols[0]
        else:
            raise ValueError("No numeric production column found in Saudi dataset")
    df = df[["date", prod_col]].rename(columns={prod_col: "saudi_production"})
    # Drop duplicate dates to avoid issues with resampling (e.g. multiple rows for the same year)
    df = df.drop_duplicates(subset="date")
    return df


def prepare_brent(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare the Brent price DataFrame.

    Renames the first numeric column to `brent_price` and parses the date.
    """
    df = df.copy()
    # Determine date column heuristically
    date_col = None
    for c in df.columns:
        if "date" in c.lower() or "time" in c.lower():
            date_col = c
            break
    if date_col is None:
        date_col = df.columns[0]
    df["date"] = pd.to_datetime(df[date_col])
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        price_col = numeric_cols[0]
    else:
        raise ValueError("No numeric price column found in Brent dataset")
    df = df[["date", price_col]].rename(columns={price_col: "brent_price"})
    df = transforms.resample_to_month_start(df, "date", ["brent_price"], how="mean")
    return df


def build_features() -> pd.DataFrame:
    """Main routine to build the feature matrix and save it to disk.

    Returns:
        The processed DataFrame ready for model training.
    """
    setup_logging(Path("logs"))
    logger.info("Building feature matrix...")

    # Load and clean datasets
    world_df = loaders.load_world_primary_energy(RAW_DATA_DIR)
    world_df = cleaning.clean_world_primary_energy(world_df)
    world_df = aggregate_world_energy(world_df)

    renew_df = loaders.load_renewables(RAW_DATA_DIR)
    renew_df = cleaning.clean_renewables(renew_df)
    renew_df = aggregate_renewables(renew_df)

    # Load Saudi crude data and filter to "Total" production BEFORE cleaning
    saudi_df = loaders.load_saudi_crude(RAW_DATA_DIR)
    # Filter to only "Total" production indicator (before column names are lowercased)
    if 'Production Indicator' in saudi_df.columns:
        saudi_df = saudi_df[saudi_df['Production Indicator'] == 'Total']
    saudi_df = cleaning.clean_saudi_crude(saudi_df)
    saudi_df = prepare_saudi_production(saudi_df)
    # Interpolate annual data to monthly by forward filling
    saudi_df = transforms.resample_to_month_start(saudi_df, "date", ["saudi_production"], how="ffill")

    # Attempt to load Brent prices; if reading Excel fails, skip and create placeholder
    try:
        brent_df = loaders.load_brent_monthly(RAW_DATA_DIR)
        brent_df = prepare_brent(brent_df)
    except Exception as exc:
        logger.warning("Could not load Brent data: %s. Using placeholder zeros.", exc)
        # Create a placeholder DataFrame with same dates as Saudi production and NaN values
        brent_df = saudi_df[["date"]].copy()
        brent_df["brent_price"] = 0.0

    # Merge all datasets on date
    df = saudi_df.merge(brent_df, on="date", how="left")
    df = df.merge(renew_df, on="date", how="left")
    df = df.merge(world_df, on="date", how="left")
    df.sort_values("date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Forward fill missing values (simple imputation)
    df.ffill(inplace=True)

    # Add lag and rolling features for key variables
    target_col = "saudi_production"
    exogenous = [c for c in df.columns if c not in {"date", target_col}]

    # Add lags for each variable up to 6 months
    for col in [target_col] + exogenous:
        df = transforms.add_lag_features(df, col, lags=[1, 2, 3, 6, 12])
        df = transforms.add_rolling_features(df, col, windows=[3, 6, 12])

    # Drop rows with NaN values created by lags
    df.dropna(inplace=True)

    # Save processed features
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DATA_DIR / "features.csv"
    df.to_csv(output_path, index=False)
    logger.info("Saved features to %s", output_path)

    return df


if __name__ == "__main__":
    build_features()
