# GCC Oil Forecast – End-to-End ML Project

<div align="center">

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![MLflow](https://img.shields.io/badge/MLflow-tracking-0194E2)](https://mlflow.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://www.docker.com/)
[![CI](https://github.com/Nayil97/gcc-oil-forecast/workflows/CI/badge.svg)](https://github.com/Nayil97/gcc-oil-forecast/actions)

**End-to-end ML solution for forecasting crude oil production in the Gulf Cooperation Council region**

[Overview](#overview) • [Tech Stack](#tech-stack) • [Key Features](#key-features) • [Results](#results-and-key-findings) • [Notebooks](#notebooks)

</div>

---

## Overview

A production-ready data science project that forecasts monthly crude oil production for GCC countries and quantifies sensitivity to key market drivers. The project demonstrates a complete ML workflow — from raw data ingestion through feature engineering, model development, experiment tracking, and deployment via a REST API and interactive dashboard.

### Business Problem

GCC economies are heavily dependent on crude oil revenues. Reliable short-term production forecasts support hedging strategies, capital planning, and investment decisions. This project combines local production statistics with external drivers — **Brent spot prices**, **renewable energy adoption**, and **global energy consumption** — to predict Saudi crude output up to six months ahead and explain what drives those forecasts.

---

## Tech Stack

| Area | Tools |
|---|---|
| **ML & Modelling** | LightGBM, XGBoost, Random Forest, scikit-learn, SHAP |
| **Data** | pandas, NumPy, EIA / OWID / SAMA datasets |
| **Experiment Tracking** | MLflow (experiment logging, model registry, artifact storage) |
| **API** | FastAPI, Uvicorn, Pydantic |
| **Dashboard** | Streamlit, Plotly |
| **Testing & Quality** | PyTest, Ruff, CI via GitHub Actions |
| **Deployment** | Docker, docker-compose |
| **Language** | Python 3.10+ |

---

## Key Features

- **Full ML pipeline** — data loading, cleaning, feature engineering, training, validation, and deployment are all modularised and testable.
- **72 engineered features** — price lags, rolling statistics, seasonal indicators, renewable energy metrics, and global demand proxies.
- **Model explainability** — SHAP values provide global and local explanations, including price elasticity estimates.
- **MLOps-ready** — experiments logged to MLflow, models versioned in the registry, and served via a REST API with Pydantic validation.
- **Interactive dashboard** — Streamlit app for scenario planning, EDA, and forecast visualisation.
- **Code quality** — Ruff linting, PyTest test suite, structured logging, and CI on every push.

---

## Results and Key Findings

### Model Performance

The LightGBM model, selected via time-series cross-validation, achieves the following metrics:

| Horizon | RMSE (mbbl/day) | MAE (mbbl/day) | Notes |
|---------|----------------|----------------|-------|
| 1 month | 2.88 | 2.74 | Strong short-term accuracy |
| 3 months | ~3.5 – 4.0 | ~3.2 – 3.8 | Good medium-term forecasts |
| 6 months | ~5.0 – 6.0 | ~4.5 – 5.5 | Reasonable long-term estimates |

*Full experiment runs and hyperparameter logs are stored in MLflow.*

### Key Insights from SHAP Analysis

1. **Brent oil price** is the strongest predictor (~35–40% of explained variance).
2. **Lagged production values** capture autocorrelation and seasonal patterns.
3. **Renewable energy growth** shows a negative correlation with crude production.
4. **Global energy demand** positively influences production forecasts.
5. **Price elasticity**: a 10% rise in Brent prices corresponds to a ~2–3% production increase (non-linear relationship).

### Feature Groups

The model uses **72 engineered features** across five groups:

- Price features (12): lags, rolling means, volatility
- Production lags (12): 1–12 month historical values
- Renewable energy indicators (12): capacity and generation metrics
- Global demand proxies (12): world primary energy consumption
- Calendar features (4): month, quarter, seasonality indicators

---

## Project Structure

```
.
├─ docker/               # Dockerfiles and compose
├─ data/                 # Raw, interim, and processed data
├─ notebooks/            # Step-by-step Jupyter notebooks
├─ src/                  # Source code: data, features, models, evaluation, utils
├─ api/                  # FastAPI application
├─ app/                  # Streamlit application
├─ mlflow/               # MLflow helper scripts
├─ tests/                # PyTest test suite
├─ docs/                 # Architecture diagrams, model card, additional docs
├─ pyproject.toml        # Dependencies and tool configuration
└─ README.md             # This file
```

---

## Notebooks

Six self-contained notebooks walk through the full workflow in order:

1. **01_data_collection_cleaning.ipynb** – ingest raw datasets, clean and harmonise them.
2. **02_eda_visualization.ipynb** – explore trends and correlations with interactive plots.
3. **03_feature_engineering.ipynb** – create lags, rolling statistics, and other features.
4. **04_model_training_tuning.ipynb** – train and tune multiple models; track experiments with MLflow.
5. **05_validation_shap.ipynb** – evaluate forecasts, compute error metrics, and explain models with SHAP.
6. **06_deployment_integration.ipynb** – package the trained model and integrate with FastAPI and Streamlit.

---

## Data Sources

Raw data is stored under `data/raw/`. Processed and feature-ready datasets are saved under `data/interim/` and `data/processed/`.

| Dataset | Source |
|---|---|
| Saudi crude oil production | SAMA annual reports |
| Brent spot prices (monthly & daily) | EIA |
| World primary energy consumption | OWID |
| Renewable energy capacity & generation | OWID |

- Total dataset size: ~25 MB raw, ~98 KB processed features.
- Data loaders are in `src/data/loaders.py`.

---

## Code Quality and Testing

- **Ruff** enforces a consistent code style and catches common errors.
- **PyTest** covers data loading, feature generation, modelling, and the API endpoints.
- **GitHub Actions CI** runs linting and tests on every push.
- **Structured logging** via `src/logging_conf.py` for debugging and auditability.

---

## Dashboard and API

### Interactive Streamlit Dashboard

- **Home** — 6-month production forecast with key metrics at a glance.
- **EDA** — interactive visualisations of historical trends, correlations, and distributions.
- **Features** — overview of all 72 engineered features including lags and rolling statistics.
- **Modelling** — side-by-side performance comparison of LightGBM, XGBoost, Random Forest, and Linear models.
- **Explainability** — SHAP feature importance and individual prediction breakdowns.
- **Forecast Scenarios** — interactive scenario planner for custom Brent price, renewables, and demand inputs.

### REST API (FastAPI)

- Real-time prediction endpoint with confidence intervals.
- Health check and monitoring endpoints.
- Request/response validation with Pydantic schemas.
- Auto-generated interactive API documentation at `/docs`.

### MLflow Tracking UI

- Full experiment history with hyperparameter and metric logs.
- Model versioning and artifact storage.
- Metric comparison charts (RMSE, MAE, R²).

---

## Limitations

**Data constraints:**
- Annual Saudi production data interpolated to monthly frequency (introduces smoothing).
- Historical data through 2023–2024; recent geopolitical events may not be captured.
- Missing values in some exogenous variables handled via forward-fill.

**Model limitations:**
- Assumes historical patterns continue; structural breaks (policy changes, OPEC+ decisions) are not explicitly modelled.
- Does not incorporate real-time news, sentiment, or political risk factors.
- Trained specifically for Saudi Arabia; retraining required for other GCC countries.

**Responsible AI:**
- Forecasts are intended as decision-support tools, not the sole basis for financial or policy decisions.
- SHAP explanations should be reviewed by domain experts.
- Energy transition dynamics evolve rapidly; quarterly retraining is recommended.

---

## Future Enhancements

- [ ] Incorporate real-time news/sentiment analysis via NLP
- [ ] Add ensemble methods (stacking, blending)
- [ ] Implement LSTM / Transformer architectures
- [ ] Extend to multi-country forecasting (UAE, Kuwait, Qatar)
- [ ] Integrate with cloud ML platforms (AWS SageMaker, Azure ML)
- [ ] Add automated retraining pipeline with data drift detection

---

## Contributing

Contributions and suggestions are welcome. Please open an issue or pull request on GitHub.

## License

Released under the MIT License. See the `LICENSE` file for details.
