"""Home page of the Streamlit application.

This page provides an executive summary of the current production forecast
along with key drivers and allows users to navigate to deeper analyses.
"""

from __future__ import annotations

import datetime as dt
import logging
import sys
from pathlib import Path
from typing import List

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import requests

# Add parent directory to path for imports
root_dir = Path(__file__).resolve().parents[1]
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))

from config import PORT_API


logger = logging.getLogger(__name__)


API_URL = f"http://localhost:{PORT_API}"


def get_next_months(n: int = 6) -> List[str]:
    """Return a list of ISO 8601 dates for the next n months."""
    today = dt.date.today().replace(day=1)
    dates = []
    for i in range(1, n + 1):
        year = today.year + (today.month + i - 1) // 12
        month = (today.month + i - 1) % 12 + 1
        dates.append(dt.date(year, month, 1).isoformat())
    return dates


def fetch_forecast(dates: List[str]) -> List[float]:
    """Call the prediction API to fetch forecasts."""
    try:
        resp = requests.post(f"{API_URL}/predict", json={"dates": dates})
        resp.raise_for_status()
        data = resp.json()
        return data.get("predictions", [])
    except Exception as exc:
        logger.error("Error fetching forecast: %s", exc)
        return []


def render_home() -> None:
    """Render the home page."""
    st.set_page_config(page_title="GCC Oil Forecast", page_icon="🛢️", layout="wide")
    st.title("🛢️ Saudi Oil Production Forecast")
    st.markdown("ML-powered forecasting system for Saudi crude oil production")
    
    # Quick forecast preview
    dates = get_next_months(6)
    preds = fetch_forecast(dates)
    
    if preds:
        # Create DataFrame
        df = pd.DataFrame({
            "Date": pd.to_datetime(dates),
            "Production": preds
        })
        
        # Metrics row
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Next Month", f"{preds[0]:.0f} MBPD")
        
        with col2:
            st.metric("6-Month Average", f"{sum(preds)/len(preds):.0f} MBPD")
        
        with col3:
            trend = preds[-1] - preds[0]
            st.metric("Trend", f"{trend:+.0f} MBPD", delta=f"{(trend/preds[0]*100):+.1f}%")
        
        # Table view
        st.subheader("📅 6-Month Forecast")
        
        display_df = df.copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%b %Y")
        display_df["Production (MBPD)"] = display_df["Production"].round(1)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": st.column_config.TextColumn("Date", width="medium"),
                "Production (MBPD)": st.column_config.NumberColumn(
                    "Production (MBPD)",
                    format="%.1f",
                    width="medium"
                )
            }
        )
    else:
        st.warning("⚠️ API not running. Start with: `python api_simple.py`")
    
    # Simple navigation guide
    st.markdown("---")
    st.subheader("📍 Explore the Dashboard")
    
    st.markdown("""
    Use the sidebar to navigate between pages:
    
    - **📊 EDA** - Explore historical data patterns and correlations
    - **⚙️ Features** - View engineered features (lags, rolling windows)
    - **🤖 Modeling** - Compare 4 models across forecast horizons
    - **🔍 Explainability** - SHAP analysis showing feature importance
    - **📈 Forecasts** - Generate custom scenarios and predictions
    """)


if __name__ == "__main__":
    render_home()
