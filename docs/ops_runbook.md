# Operations Runbook

This document serves as a quick reference for deploying, monitoring and maintaining the GCC Oil Forecast application in production environments.

## Environment Configuration

The application behaviour is controlled by the following environment variables:

| Variable                | Default              | Description                                                |
|-------------------------|----------------------|------------------------------------------------------------|
| `MLFLOW_TRACKING_URI`   | `http://mlflow:5000` | URL of the MLflow tracking server.                         |
| `MLFLOW_EXPERIMENT_NAME`| `gcc_oil_forecast`   | Name of the MLflow experiment to log runs under.          |
| `MODEL_REGISTRY_STAGE`  | `Production`         | Stage from which to pull registered models (e.g., Staging).|
| `PORT_API`              | `8000`               | Port the FastAPI server listens on.                       |
| `PORT_APP`              | `8501`               | Port the Streamlit app listens on.                        |

These variables can be supplied via a `.env` file or directly in docker‑compose.  The `.env` file is not committed to version control.

## Running Locally

For local development without Docker, perform the following steps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[dev]

# Start MLflow tracking server
bash mlflow/mlflow.sh &

# Build features and train models
python -m src.features.build_features
python -m src.models.train

# Start API and Streamlit
uvicorn api.main:app --reload --port ${PORT_API:-8000} &
streamlit run app/Home.py --server.port ${PORT_APP:-8501}
```

Use `source .env` to export environment variables before running the above commands.

## Running with Docker Compose

The recommended method for deployment is via Docker Compose.  Run the following from the project root:

```bash
docker compose -f docker/docker-compose.yml up --build
```

This will start the MLflow server, API and Streamlit app in separate containers.  Use `docker compose down` to stop the services.

## Monitoring

- **API health:** the API exposes a `/health` endpoint that returns a simple status check.  Use this in your monitoring system to ensure the API is responsive.
- **MLflow UI:** open `http://localhost:5000` in a browser to access the MLflow tracking UI.  You can view experiments, runs and registered models.
- **Logging:** application logs are emitted to stdout and a rotating file via the configuration in `src/logging_conf.py`.  Centralise logs using your platform of choice (e.g., ELK stack).

## Updating Models

1. Update the data by placing new files into `data/raw/` and re‑running the feature engineering and training scripts.
2. Promote the desired model version in the MLflow UI to the stage specified by `MODEL_REGISTRY_STAGE` (e.g., `Production`).
3. Restart the API container to load the new model from the registry.  The Streamlit app will automatically display updated predictions.

## Backup and Recovery

MLflow uses an SQLite database in the default configuration.  For production deployments consider using a more robust backend store (e.g., PostgreSQL) and configure the `MLFLOW_BACKEND_STORE_URI` accordingly.  Regularly backup the database and the `mlruns/` directory containing artefacts.

## Troubleshooting

- **API returns 500 error:** Check the API logs for stack traces.  Common issues include missing model artefacts or invalid input payloads.
- **Model not found:** Ensure that a model for the requested horizon is registered in MLflow under the expected stage.  Use the MLflow UI to verify.
- **Port conflicts:** Adjust `PORT_API` and `PORT_APP` in your `.env` file or docker‑compose override.
