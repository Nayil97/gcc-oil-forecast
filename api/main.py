"""FastAPI application for GCC oil forecasting."""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path for imports
root_dir = Path(__file__).resolve().parents[1]
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))
if str(root_dir / "api") not in sys.path:
    sys.path.insert(0, str(root_dir / "api"))

from schemas import PredictRequest, PredictResponse, WhatIfRequest, WhatIfResponse, ModelInfo  # noqa: E402
from logging_conf import setup_logging  # noqa: E402
from models.forecast import Forecaster  # noqa: E402
from models.registry import get_model_metadata  # noqa: E402


setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(title="GCC Oil Forecast API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest) -> PredictResponse:
    """Return predictions for the specified dates and optional scenario."""
    try:
        # Determine horizon as the number of months between today and first prediction date
        dates = req.dates
        if not dates:
            raise HTTPException(status_code=400, detail="At least one date must be provided.")
        # Use horizon based on first date difference; default to 1 month
        _ = datetime.fromisoformat(dates[0])  # Validate date format
        # Compute month difference from last known date; fallback to 1 if negative
        horizon = 1
        forecaster = Forecaster(horizon)
        predictions = forecaster.predict(dates=dates, scenario=req.scenario)
        return PredictResponse(predictions=predictions)
    except Exception as exc:
        logger.exception("Prediction failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/model/{h}/info", response_model=ModelInfo)
async def model_info(h: int) -> ModelInfo:
    """Return metadata about the current model for horizon h."""
    try:
        meta = get_model_metadata(prefix=f"gcc_oil_forecast_h{h}")
        return ModelInfo(
            horizon=h,
            run_id=meta["run_id"],
            version=str(meta["version"]),
            # additional metrics could be retrieved from MLflow run metadata
        )
    except Exception as exc:
        logger.exception("Model info retrieval failed: %s", exc)
        raise HTTPException(status_code=404, detail=str(exc))


@app.post("/whatif", response_model=WhatIfResponse)
async def what_if(req: WhatIfRequest) -> WhatIfResponse:
    """Perform a simple what‑if analysis for a single date.

    Returns the baseline prediction for the given date and the predictions
    when the specified variable is set to each of the provided values.
    """
    try:
        date = req.date
        variable = req.variable
        values = req.values
        # Use horizon of 1 month for what‑if analysis
        horizon = 1
        forecaster = Forecaster(horizon)
        # Baseline prediction uses no scenario override
        baseline_pred = forecaster.predict(dates=[date])[0]
        # Generate scenario predictions
        scenario = {variable: values}
        preds = forecaster.predict(dates=[date] * len(values), scenario=scenario)
        return WhatIfResponse(
            baseline_prediction=baseline_pred,
            variable=variable,
            values=values,
            predictions=preds,
        )
    except Exception as exc:
        logger.exception("What‑if analysis failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
