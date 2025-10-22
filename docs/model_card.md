# Model Card: GCC Oil Forecast

## Model Overview

This model predicts monthly crude oil production for Saudi Arabia up to six months into the future.  It is trained on historical production data together with exogenous features such as Brent spot prices, renewable energy capacity and global primary energy consumption.  The goal of the model is to provide actionable forecasts and quantify how sensitive production is to changes in external drivers.

## Intended Use

- **Primary users:** analysts, traders and planners within GCC national oil companies and related ministries.
- **Primary use cases:** hedging and pricing strategies, production planning, and macro‑economic forecasting.
- **Not suitable for:** predicting production for non‑GCC countries without retraining; making political or regulatory decisions.

## Data

| Source                                        | Description                                                     |
|-----------------------------------------------|-----------------------------------------------------------------|
| Saudi crude oil production (SAMA statistics)  | Annual production figures for Saudi Arabia since 1970.          |
| OWID renewable energy dataset                 | Installed capacity and electricity generation by country.       |
| OWID world primary energy dataset            | Primary energy consumption and production for all countries.    |
| EIA Brent spot price (monthly and daily)      | Benchmark oil prices used as price drivers.                     |

All datasets are cleaned and aligned to a monthly frequency.  Annual data are interpolated to monthly using linear interpolation with cautionary notes documented in the code and notebooks.

## Features

- **Price features:** raw Brent price, percentage changes, lagged values (1–12 months), rolling means and volatility measures.
- **Renewable energy features:** installed capacity and electricity generation (levels, growth rates, lags).  These capture the energy transition effect on production.
- **Demand proxies:** world primary energy indicators and economic growth proxies, capturing global demand for oil.
- **Calendar features:** month, quarter, whether the month falls in summer vs winter, Ramadan flags.
- **Lagged production:** previous values of Saudi production to capture autocorrelation and seasonality.

## Training and Validation

The primary model is a gradient boosting regressor (LightGBM) with a quantile objective to estimate prediction intervals.  Secondary models include CatBoost and ElasticNet for benchmarking.  Hyperparameters are tuned using Optuna with a time‑series split to prevent leakage.  Backtesting is performed with rolling origins for horizons 1–6 months.

Metrics used for evaluation include:

- **Root Mean Squared Error (RMSE)** – to penalise large errors.
- **Symmetric Mean Absolute Percentage Error (sMAPE)** – scale‑independent comparison across horizons.
- **Pinball loss / interval coverage** – for evaluating quantile predictions and prediction interval calibration.

## Performance Summary

Below is an illustrative summary of performance (exact numbers will depend on the latest training run recorded in MLflow):

- **Horizon 1 month:** RMSE ~ 0.15 mbbl/day; sMAPE ~ 2.1 %
- **Horizon 3 months:** RMSE ~ 0.25 mbbl/day; sMAPE ~ 3.4 %
- **Horizon 6 months:** RMSE ~ 0.40 mbbl/day; sMAPE ~ 5.5 %

The model exhibits low error at short horizons with gradually increasing uncertainty at longer horizons.  Prediction intervals capture the majority of true values within the 80 % and 95 % confidence bands.

## Explainability

SHAP (SHapley Additive exPlanations) is used to interpret the model.  The following insights have been observed:

- **Brent price:** the most important feature across horizons; increases in price generally lead to higher predicted production with diminishing returns.
- **Lagged production:** strong autocorrelation is present; production two months ago has a significant positive contribution.
- **Renewables growth:** higher renewable capacity growth tends to reduce crude production, reflecting the energy transition in the region.
- **World energy demand:** positive relationship; higher global energy consumption results in higher crude production forecasts.

Global SHAP values are visualised as bar charts, while temporal SHAP heatmaps show how feature importance evolves over time.

## Limitations and Considerations

- **Data availability:** some datasets (e.g., Brent prices) have missing values or require interpolation.  Annual series interpolated to monthly should be used cautiously.
- **Structural breaks:** geopolitical events, policy changes and technological disruptions are not explicitly encoded and may cause sudden shifts not captured by historical patterns.
- **Generalisation:** the model is tailored for Saudi production.  Applying it to other countries or commodities would require retraining and feature re‑engineering.
- **Ethical considerations:** forecasts should be used responsibly and not as the sole basis for decisions that could impact energy markets or national economies.
