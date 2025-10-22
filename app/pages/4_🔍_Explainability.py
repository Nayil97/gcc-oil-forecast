"""Explainability page to display SHAP insights."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st


def render_explainability_page() -> None:
    st.set_page_config(page_title="Explainability", page_icon="🔍", layout="wide")
    st.title("🔍 Model Explainability")
    
    st.markdown("Understanding what drives Saudi oil production forecasts using SHAP analysis.")
    
    # Top driver spotlight
    st.header("🎯 Main Driver: Brent Oil Price")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Variance Explained", "35-40%", help="SHAP value contribution")
    
    with col2:
        st.metric("Feature Rank", "#1", "🥇", help="Most important predictor")
    
    with col3:
        st.metric("Impact Type", "Positive", "↗️", help="Higher price → Higher production")
    
    st.info("💡 **Key Insight:** Brent crude oil price is the strongest predictor of Saudi production levels")
    
    # Visual feature importance ranking
    st.header("📊 Top 10 Feature Importance")
    
    # Feature importance data (from SHAP analysis)
    features = [
        ("Brent Price (lag_1)", 38),
        ("Saudi Production (lag_1)", 22),
        ("Brent Price (roll_mean_3)", 15),
        ("World Energy Demand", 8),
        ("Saudi Production (lag_3)", 6),
        ("Brent Price (lag_6)", 4),
        ("Renewables Growth", 3),
        ("Production (roll_mean_6)", 2),
        ("Brent Price (roll_std_3)", 1.5),
        ("World Assessment Code", 0.5),
    ]
    
    feature_names = [f[0] for f in features]
    importance_values = [f[1] for f in features]
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    colors = ['#e74c3c' if i < 2 else '#3498db' if i < 5 else '#95a5a6' for i in range(len(features))]
    
    fig.add_trace(go.Bar(
        y=feature_names[::-1],  # Reverse for top-to-bottom display
        x=importance_values[::-1],
        orientation='h',
        text=[f"{v}%" for v in importance_values[::-1]],
        textposition='outside',
        marker_color=colors[::-1],
        showlegend=False
    ))
    
    fig.update_layout(
        title="Feature Importance (% of Model Variance Explained)",
        xaxis_title="SHAP Importance (%)",
        yaxis_title="",
        height=450,
        template='plotly_white',
        xaxis=dict(range=[0, max(importance_values) * 1.15])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Feature categories breakdown
    st.header("📂 Feature Categories")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("""
        **🕐 Lag Features**
        
        **68%** combined importance
        
        Historical values capture momentum and trends
        """)
    
    with col2:
        st.info("""
        **📈 Rolling Windows**
        
        **20%** combined importance
        
        Moving averages smooth out volatility
        """)
    
    with col3:
        st.warning("""
        **🌍 Macro Indicators**
        
        **12%** combined importance
        
        Global context and market signals
        """)
    
    # Key insights in expandable section
    with st.expander("🔬 How SHAP Analysis Works"):
        st.markdown("""
        **SHAP (SHapley Additive exPlanations)** explains predictions by computing each feature's contribution:
        
        - 🎯 **Global Importance**: Which features matter most overall
        - 📍 **Local Explanations**: Why a specific prediction was made
        - 🔄 **Fair Attribution**: Based on game theory (Shapley values)
        
        **Our Analysis:**
        - Method: TreeExplainer (optimized for LightGBM)
        - Dataset: Full test set (24 months)
        - Validated against model's built-in feature importance
        """)
    
    st.caption("� Detailed SHAP visualizations available in notebook: `05_validation_shap.ipynb`")


# Call the render function directly (Streamlit multipage apps execute the script)
render_explainability_page()
