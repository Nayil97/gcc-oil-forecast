#!/bin/bash
# Quick start script for running the project locally

echo "🚀 Starting GCC Oil Forecast System..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check for required processes
API_RUNNING=$(pgrep -f "api_simple.py" | wc -l)
MLFLOW_RUNNING=$(pgrep -f "mlflow server" | wc -l)

# Start API if not running
if [ $API_RUNNING -eq 0 ]; then
    echo "🔧 Starting API on port 8000..."
    nohup python api_simple.py > api.log 2>&1 &
    sleep 2
else
    echo "✅ API already running"
fi

# Start MLflow if not running
if [ $MLFLOW_RUNNING -eq 0 ]; then
    echo "📊 Starting MLflow on port 5000..."
    nohup mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns > mlflow.log 2>&1 &
    sleep 2
else
    echo "✅ MLflow already running"
fi

echo ""
echo "✨ Services started successfully!"
echo ""
echo "📍 URLs:"
echo "   - Streamlit: http://localhost:8501 (run: streamlit run app/Home.py --server.port 8501)"
echo "   - API:       http://localhost:8000"
echo "   - MLflow:    http://localhost:5000"
echo ""
echo "🛑 To stop: pkill -f 'api_simple.py|mlflow server'"
echo ""

# Optionally start Streamlit
read -p "Start Streamlit now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    streamlit run app/Home.py --server.port 8501
fi
