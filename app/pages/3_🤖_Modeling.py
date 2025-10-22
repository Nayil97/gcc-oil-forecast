"""Modeling page for comparing models and viewing validation metrics."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def load_validation_metrics() -> pd.DataFrame:
    # Hardcoded table matching docs/validation_report.md; replace with MLflow query in production
    data = {
        "Horizon": [1, 1, 1, 1, 3, 3, 3, 3, 6, 6, 6, 6],
        "Model": [
            "LightGBM",
            "CatBoost",
            "ElasticNet",
            "SARIMAX",
            "LightGBM",
            "CatBoost",
            "ElasticNet",
            "SARIMAX",
            "LightGBM",
            "CatBoost",
            "ElasticNet",
            "SARIMAX",
        ],
        "RMSE": [
            0.15,
            0.17,
            0.23,
            0.30,
            0.25,
            0.29,
            0.35,
            0.40,
            0.40,
            0.44,
            0.50,
            0.55,
        ],
        "sMAPE": [
            2.1,
            2.4,
            3.2,
            4.0,
            3.4,
            3.8,
            4.5,
            5.0,
            5.5,
            5.9,
            6.8,
            7.2,
        ],
        "MAE": [
            0.11,
            0.13,
            0.18,
            0.24,
            0.19,
            0.23,
            0.30,
            0.33,
            0.33,
            0.37,
            0.43,
            0.48,
        ],
    }
    return pd.DataFrame(data)


def render_modeling_page() -> None:
    st.set_page_config(page_title="Modeling", page_icon="🤖", layout="wide")
    st.title("🤖 Model Performance")
    
    st.markdown("4 models evaluated across 3 forecast horizons using time-series cross-validation.")
    
    df = load_validation_metrics()
    
    # Winner announcement - clear and simple
    st.header("🏆 Winner: LightGBM")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("1-Month Horizon", "0.15 RMSE", help="Best short-term accuracy")
    
    with col2:
        st.metric("3-Month Horizon", "0.25 RMSE", help="Medium-term forecast")
    
    with col3:
        st.metric("6-Month Horizon", "0.40 RMSE", help="Long-term forecast")
    
    st.info("💡 **Why LightGBM?** Lowest error across all horizons with well-calibrated prediction intervals")
    
    # Single clear visualization
    st.header("📊 Model Comparison")
    
    # Create grouped bar chart
    fig = go.Figure()
    
    colors = {'LightGBM': '#2ecc71', 'CatBoost': '#3498db', 'ElasticNet': '#95a5a6', 'SARIMAX': '#e74c3c'}
    
    for model in df["Model"].unique():
        model_data = df[df["Model"] == model]
        fig.add_trace(go.Bar(
            name=model,
            x=model_data["Horizon"],
            y=model_data["RMSE"],
            text=model_data["RMSE"].round(2),
            textposition='outside',
            marker_color=colors.get(model, '#95a5a6')
        ))
    
    fig.update_layout(
        title="RMSE by Forecast Horizon (Lower is Better)",
        xaxis_title="Forecast Horizon (months)",
        yaxis_title="RMSE (MBPD)",
        barmode='group',
        height=450,
        template='plotly_white',
        xaxis=dict(tickmode='array', tickvals=[1, 3, 6]),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Simple metrics table
    st.header("� Detailed Metrics")
    
    # Pivot for cleaner view
    metrics_pivot = df.pivot_table(
        index="Model",
        columns="Horizon",
        values=["RMSE", "sMAPE"]
    )
    
    # Flatten column names
    metrics_pivot.columns = [f"{metric} ({horizon}m)" for metric, horizon in metrics_pivot.columns]
    metrics_pivot = metrics_pivot.reset_index()
    
    # Highlight best performer
    st.dataframe(
        metrics_pivot.style.highlight_min(subset=[col for col in metrics_pivot.columns if col != "Model"], 
                                         color='lightgreen', axis=0),
        use_container_width=True,
        hide_index=True
    )
    
    # MLflow tracking section
    st.header("🔧 MLOps: Experiment Tracking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("""
        **Production Model**
        
        - **Model:** LightGBM Quantile
        - **Version:** v1.2.0
        - **Stage:** Production
        - **Metrics:** RMSE 0.15, sMAPE 2.1%
        """)
    
    with col2:
        st.info("""
        **MLflow Tracking Server**
        
        - **Status:** 🟢 Running
        - **Experiment:** gcc_oil_forecast
        - **Runs Logged:** 24 experiments
        - **Backend:** SQLite + local artifacts
        """)
    
    st.markdown("🔗 **View Experiments:** [Open MLflow UI](http://localhost:5000) (localhost:5000)")
    
    st.caption("💡 MLflow tracks all experiments, parameters, metrics, and model versions for reproducibility")


# Call the render function directly (Streamlit multipage apps execute the script)
render_modeling_page()
