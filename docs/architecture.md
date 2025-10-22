# System Architecture

This document describes the high‑level architecture of the GCC Oil Forecast project and how the various components interact to deliver a production‑ready forecasting pipeline.

## Overview

The solution is built around a modular architecture that separates data processing, model training and serving, and user interface concerns.  The following components are involved:

* **Data ingestion and cleaning** – Python scripts load the raw datasets (energy statistics, oil production, price benchmarks) from CSV/ZIP/XLS files in `data/raw/`.  Cleaning functions harmonise column names, parse dates and interpolate annual series to monthly frequency.
* **Feature engineering** – Transformations such as lag creation, rolling statistics and calendar features are applied.  The engineered features are saved to `data/processed/` for reuse.
* **Model training and tracking** – Multiple machine‑learning models (LightGBM, CatBoost and ElasticNet) are trained using time‑series cross‑validation.  Hyperparameters are tuned with Optuna and the results are logged to an MLflow tracking server.
* **Model registry** – The best models are registered in MLflow.  The API can fetch the champion model for a given prediction horizon from the registry.
* **FastAPI service** – A RESTful API provides endpoints for single and batch forecasts (`/predict`) and metadata about the current model (`/model/{h}/info`).  The API loads models from the registry and preprocesses incoming data to ensure compatibility with the training pipeline.
* **Streamlit application** – A user‑friendly dashboard allows stakeholders to explore the data (EDA), inspect engineered features, compare model performance, view SHAP explainability plots and generate new forecasts under different scenarios.
* **Docker and docker‑compose** – All services (API, Streamlit and MLflow) are containerised to ensure portability and reproducibility across environments.

## Data Flow

```text
            ┌───────────────────┐
            │ Raw data in CSV/  │
            │ ZIP/XLS files     │
            └─────────┬─────────┘
                      │
              Data loaders (src/data/loaders.py)
                      │
            ┌─────────▼─────────┐
            │ Cleaning &        │
            │ harmonisation     │
            │ (src/data/cleaning.py)
            └─────────┬─────────┘
                      │
              Feature engineering
            (src/features/build_features.py)
                      │
            ┌─────────▼─────────┐
            │ Processed dataset │
            │ (data/processed/) │
            └─────────┬─────────┘
                      │
              Model training & tuning
            (src/models/train.py)
                      │
            ┌─────────▼─────────┐
            │ MLflow experiments│
            │ and model registry│
            └─────────┬─────────┘
                      │
              ┌───────▼───────┐
              │ Prediction API│
              │ (FastAPI)     │
              └───────┬───────┘
                      │
              ┌───────▼───────┐
              │ Streamlit app │
              └───────────────┘
```

## Component Responsibilities

### Data Layer

The `src/data/` package encapsulates all logic related to ingesting and cleaning the datasets.  The loaders hide the complexities of dealing with ZIP archives and Excel files.  Cleaning functions standardise column names and date formats, while transformation utilities handle resampling and creating lags and rolling features.

### Feature Layer

In `src/features/` the engineered features are constructed.  This step merges the cleaned datasets on the monthly date index and applies domain‑informed transformations such as differencing and growth rates.  The resulting feature matrix can be consumed by any model.

### Modelling Layer

`src/models/` contains everything related to model training, evaluation and inference.  Models are trained with time‑aware cross‑validation and hyperparameter optimisation.  Results and artefacts are logged to MLflow and the best model for each horizon is promoted to the registry.

### API & UI

The FastAPI application in `api/` provides a simple REST interface for obtaining predictions and model metadata.  It wraps the pre‑processing pipeline and loads the appropriate model from the registry.  The Streamlit application in `app/` consumes these endpoints to deliver interactive dashboards for data exploration, feature inspection, modelling insights and forecasting.

### Orchestration

Dockerfiles and docker‑compose definitions live in the `docker/` directory.  These scripts define how to build and run the MLflow server, API server and Streamlit front‑end in isolated containers.  Environment variables can be passed via a `.env` file or docker‑compose overrides to customise the setup.
