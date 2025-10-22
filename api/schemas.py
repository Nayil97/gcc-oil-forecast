"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """Request schema for /predict endpoint."""

    dates: List[str] = Field(
        ..., min_length=1, description="List of ISO 8601 dates (YYYY-MM-DD) to forecast."
    )
    scenario: Optional[Dict[str, List[float]]] = Field(
        default=None,
        description="Optional scenario values keyed by feature name; each list must align with dates.",
    )


class PredictResponse(BaseModel):
    """Response schema for /predict endpoint."""

    predictions: List[float]
    intervals: Optional[Dict[str, List[float]]] = None


class WhatIfRequest(BaseModel):
    """Request schema for /whatif endpoint."""

    date: str = Field(..., description="Date for which to perform scenario analysis (YYYY-MM-DD)")
    variable: str = Field(..., description="Name of the feature to vary")
    values: List[float] = Field(
        ..., min_length=1, description="List of values to substitute for the feature"
    )


class WhatIfResponse(BaseModel):
    """Response schema for /whatif endpoint."""

    baseline_prediction: float
    variable: str
    values: List[float]
    predictions: List[float]


class ModelInfo(BaseModel):
    """Schema for model metadata returned by /model/{h}/info."""

    horizon: int
    run_id: str
    version: str
    rmse: Optional[float] = None
    mae: Optional[float] = None
    smape: Optional[float] = None
    trained_at: Optional[str] = None
    features: Optional[List[str]] = None