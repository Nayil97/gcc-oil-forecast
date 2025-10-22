"""Forecasts dashboard page."""

from __future__ import annotations

import datetime as dt
import logging
import sys
from pathlib import Path
from typing import Dict, List

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


def call_predict(dates: List[str], scenario: Dict[str, List[float]]) -> List[float]:
    try:
        resp = requests.post(f"{API_URL}/predict", json={"dates": dates, "scenario": scenario})
        resp.raise_for_status()
        return resp.json().get("predictions", [])
    except Exception as exc:
        logger.error("Forecast API call failed: %s", exc)
        return []


def render_dashboard() -> None:
    st.set_page_config(page_title="Forecasts Dashboard", page_icon="📈", layout="wide")
    st.title("📈 Production Forecast")

    st.markdown("Generate Saudi oil production forecasts under different scenarios.")

    # Layout: Left side = inputs, Right side = results
    col_input, col_output = st.columns([1, 2])
    
    with col_input:
        st.subheader("📅 Forecast Settings")
        
        # Date picker for starting month and horizon
        today = dt.date.today().replace(day=1)
        start_date = st.date_input(
            "Start month", value=today, format="YYYY-MM-DD"
        )
        horizon = st.slider("Horizon (months)", min_value=1, max_value=12, value=6, help="Number of months to forecast")
        
        dates = []
        for i in range(horizon):
            year = start_date.year + (start_date.month + i - 1) // 12
            month = (start_date.month + i - 1) % 12 + 1
            dates.append(dt.date(year, month, 1).isoformat())

        st.subheader("🎛️ Scenario Inputs")
        
        brent = st.slider(
            "Brent Price ($/bbl)", 
            min_value=40.0, 
            max_value=150.0, 
            value=90.0,
            step=5.0,
            help="Average Brent crude oil price"
        )
        
        renew_growth = st.slider(
            "Renewables Growth (%)", 
            min_value=0.0, 
            max_value=10.0, 
            value=2.0,
            step=0.5,
            help="Annual growth rate of renewable energy"
        ) / 100  # Convert to fraction
        
        world_growth = st.slider(
            "World Energy Demand (%)", 
            min_value=-5.0, 
            max_value=5.0, 
            value=1.0,
            step=0.5,
            help="Global energy demand growth rate"
        ) / 100  # Convert to fraction
        
        generate_btn = st.button("🚀 Generate Forecast", type="primary", use_container_width=True)
    
    with col_output:
        if generate_btn:
            with st.spinner("Generating forecast..."):
                scenario = {
                    "brent_price": [brent] * horizon,
                    "renewables_installed_capacity": [renew_growth] * horizon,
                    "world_primary_energy_consumption": [world_growth] * horizon,
                }
                preds = call_predict(dates, scenario)
                
                if preds:
                    st.subheader("📊 Forecast Results")
                    
                    # Key metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Average Production", f"{sum(preds)/len(preds):.0f} MBPD")
                    
                    with col2:
                        st.metric("First Month", f"{preds[0]:.0f} MBPD")
                    
                    with col3:
                        st.metric("Last Month", f"{preds[-1]:.0f} MBPD", 
                                 delta=f"{preds[-1] - preds[0]:+.0f}")
                    
                    # Create enhanced forecast chart
                    df = pd.DataFrame({
                        "Date": pd.to_datetime(dates),
                        "Production": preds
                    })
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=df["Date"],
                        y=df["Production"],
                        mode='lines+markers',
                        name='Forecast',
                        line=dict(color='#2ecc71', width=3),
                        marker=dict(size=8),
                        fill='tozeroy',
                        fillcolor='rgba(46, 204, 113, 0.1)'
                    ))
                    
                    fig.update_layout(
                        title=f"Saudi Production Forecast ({horizon}-Month Horizon)",
                        xaxis_title="Date",
                        yaxis_title="Production (MBPD)",
                        height=400,
                        template='plotly_white',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Data table and download
                    with st.expander("📋 View forecast data"):
                        display_df = df.copy()
                        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m")
                        display_df["Production (MBPD)"] = display_df["Production"].round(1)
                        st.dataframe(display_df[["Date", "Production (MBPD)"]], 
                                   use_container_width=True, hide_index=True)
                    
                    # Download button
                    csv_data = df.copy()
                    csv_data["Date"] = csv_data["Date"].dt.strftime("%Y-%m-%d")
                    csv_data.columns = ["Date", "Forecast (MBPD)"]
                    
                    st.download_button(
                        label="⬇️ Download CSV",
                        data=csv_data.to_csv(index=False),
                        file_name=f"saudi_forecast_{dt.date.today()}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Failed to generate forecast. Make sure the API is running on port 8000.")
                    st.info("💡 **Tip:** The API should be started with `python api_simple.py`")
        else:
            # Show placeholder when no forecast generated
            st.info("👈 Configure your scenario and click **Generate Forecast** to see predictions")
            
            # Show example scenarios
            st.subheader("💡 Example Scenarios")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success("""
                **📈 High Price Scenario**
                - Brent: $120/bbl
                - World demand: +3%
                - Result: Higher production
                """)
            
            with col2:
                st.warning("""
                **📉 Energy Transition**
                - Brent: $70/bbl
                - Renewables: +5%
                - Result: Moderated production
                """)


# Call the render function directly (Streamlit multipage apps execute the script)
render_dashboard()
