"""Simplified API entry point that works around import issues."""

import sys
from pathlib import Path

# Add paths before any imports
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir / "src"))
sys.path.insert(0, str(root_dir / "api"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create a simple mock API for demo purposes
app = FastAPI(title="GCC Oil Forecast API (Demo)", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}

@app.post("/predict")
def predict(request: dict):
    """Mock predict endpoint - returns realistic Saudi production forecast."""
    dates = request.get("dates", [])
    scenario = request.get("scenario", {})
    
    # Get scenario inputs or use defaults
    brent_prices = scenario.get("brent_price", [80.0] * len(dates))
    
    # Realistic baseline: Saudi production around 2800-3200 MBPD
    baseline = 2950.0
    
    # Generate realistic predictions based on Brent price
    predictions = []
    for i, brent in enumerate(brent_prices):
        # Price effect: higher prices -> higher production
        price_effect = (brent - 75) * 2.5  # ~2.5 MBPD per dollar
        
        # Slight upward trend
        trend = i * 5
        
        # Some variation
        variation = (i % 3 - 1) * 15
        
        pred = baseline + price_effect + trend + variation
        # Keep within realistic bounds (2000-3500 MBPD)
        pred = max(2000, min(3500, pred))
        predictions.append(round(pred, 1))
    
    return {
        "predictions": predictions,
        "intervals": {
            "lower": [round(p * 0.97, 1) for p in predictions],  # -3% uncertainty
            "upper": [round(p * 1.03, 1) for p in predictions]   # +3% uncertainty
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
