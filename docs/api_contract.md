# API Contract

This document describes the REST endpoints provided by the FastAPI service.  The API acts as a thin layer over the trained model and feature pipeline.  Requests and responses use JSON for structured data interchange.

Base URL: `/`

## Endpoints

### `GET /health`

Returns a simple heartbeat to confirm that the API is running.

**Response:**

```json
{
  "status": "ok"
}
```

### `POST /predict`

Generate production forecasts for one or more future months given exogenous scenarios.  If no features are provided for a given date the API will substitute the latest available values and apply the same lags and transformations used in training.

**Request Body:**

```json
{
  "dates": ["2025-01-01", "2025-02-01", "2025-03-01"],
  "scenario": {
    "brent_price": [90.0, 92.5, 95.0],
    "renewables_growth": [0.02, 0.03, 0.04],
    "world_energy_growth": [0.01, 0.01, 0.01]
  }
}
```

**Response:**

```json
{
  "predictions": [10.5, 10.7, 10.9],
  "intervals": {
    "lower_80": [10.2, 10.4, 10.5],
    "upper_80": [10.8, 11.0, 11.3]
  }
}
```

### `GET /model/{h}/info`

Retrieve metadata about the currently deployed model for horizon `h` (integer from 1 to 6).  This includes training metrics, run ID and feature schema.  The horizon corresponds to how many months ahead the model predicts.

**Response:**

```json
{
  "horizon": 3,
  "run_id": "abcdef1234567890",
  "rmse": 0.25,
  "smape": 3.4,
  "trained_at": "2025-10-01T12:00:00Z",
  "features": [
    "brent_price",
    "brent_price_lag_1",
    "brent_price_roll_mean_3",
    "renewables_growth",
    ...
  ]
}
```

### `POST /whatif`

Perform a scenario analysis by perturbing one or more exogenous variables around their baseline and returning the corresponding change in the forecast.  This endpoint is useful for assessing sensitivity to price or renewable adoption.

**Request Body:**

```json
{
  "date": "2025-03-01",
  "variable": "brent_price",
  "values": [80, 90, 100, 110]
}
```

**Response:**

```json
{
  "baseline_prediction": 10.5,
  "variable": "brent_price",
  "values": [80, 90, 100, 110],
  "predictions": [10.1, 10.5, 10.8, 11.1]
}
```

## Error Handling

All errors are returned with a JSON body containing a `detail` field and an appropriate HTTP status code.  For example, if a request contains an invalid date format:

```json
{
  "detail": "Invalid date format.  Expected YYYY-MM-DD."
}
```
