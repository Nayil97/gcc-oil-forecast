"""Feature inspection page."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Add parent directory to path for imports
root_dir = Path(__file__).resolve().parents[1]
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))

from config import PROCESSED_DATA_DIR


def load_features() -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DATA_DIR / "features.csv", parse_dates=["date"])


def render_features_page() -> None:
    st.set_page_config(page_title="Features", page_icon="⚙️", layout="wide")
    st.title("⚙️ Feature Engineering")

    st.markdown("""
    Transforming 7 raw features into 73 engineered features for time series forecasting.
    """)

    df = load_features()
    
    # Visual transformation overview
    st.header("� Feature Transformation")
    
    import plotly.graph_objects as go
    
    # Create visual flow diagram
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.metric("� Input", "7 Base Features", help="Raw data from 3 sources")
    
    with col2:
        st.markdown("### ➡️")
        st.caption("**Engineering Pipeline**")
        st.caption("• 5 Lag Features")
        st.caption("• 6 Rolling Windows")
    
    with col3:
        st.metric("📤 Output", "73 Total Features", delta="+66", help="Ready for modeling")
    
    # Feature breakdown with visual cards
    st.header("📊 Feature Categories")
    
    base_features = [c for c in df.columns if '_lag_' not in c and '_roll_' not in c and c != 'date']
    lag_features = [c for c in df.columns if "_lag_" in c]
    rolling_features = [c for c in df.columns if "_roll_" in c]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"""
        **🔹 Base Features**
        
        {len(base_features)} features
        
        Original variables from raw data sources
        """)
        with st.expander("View base features"):
            for feat in base_features:
                st.text(f"• {feat}")
    
    with col2:
        st.success(f"""
        **🕐 Lag Features**
        
        {len(lag_features)} features
        
        Historical values (1, 2, 3, 6, 12 months ago)
        """)
        with st.expander("View by variable"):
            for var in ["saudi_production", "brent_price", "renewables_value", "world_obs_value"]:
                var_lags = [f for f in lag_features if f.startswith(var)][:3]  # Show first 3
                if var_lags:
                    st.caption(f"**{var}:**")
                    for lag in var_lags:
                        st.text(f"  • {lag}")
    
    with col3:
        st.warning(f"""
        **📈 Rolling Features**
        
        {len(rolling_features)} features
        
        Moving averages & volatility (3, 6, 12 month windows)
        """)
        with st.expander("View by variable"):
            for var in ["saudi_production", "brent_price", "renewables_value", "world_obs_value"]:
                var_rolling = [f for f in rolling_features if f.startswith(var)][:3]  # Show first 3
                if var_rolling:
                    st.caption(f"**{var}:**")
                    for roll in var_rolling:
                        st.text(f"  • {roll}")
    
    # Interactive feature exploration
    st.header("� Interactive Feature Explorer")
    
    tab1, tab2 = st.tabs(["📊 Feature Distribution", "🔍 Data Preview"])
    
    with tab1:
        st.subheader("Visualize Feature Behavior")
        
        # Interactive feature selector
        feature_cols = [c for c in df.columns if c != "date"]
        selected_feature = st.selectbox("Select a feature to visualize", feature_cols, 
                                       index=feature_cols.index("saudi_production") if "saudi_production" in feature_cols else 0)
        
        # Show statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean", f"{df[selected_feature].mean():.2f}")
        with col2:
            st.metric("Std Dev", f"{df[selected_feature].std():.2f}")
        with col3:
            st.metric("Min", f"{df[selected_feature].min():.2f}")
        with col4:
            st.metric("Max", f"{df[selected_feature].max():.2f}")
        
        # Time series plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"],
            y=df[selected_feature],
            mode='lines',
            name=selected_feature,
            line=dict(color='#1f77b4', width=2),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.1)'
        ))
        fig.update_layout(
            title=f"{selected_feature} Over Time",
            xaxis_title="Date",
            yaxis_title="Value",
            height=400,
            hovermode='x unified',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Feature Matrix Sample")
        
        # Show key columns
        key_cols = ["date", "saudi_production", "brent_price", 
                   "saudi_production_lag_1", "brent_price_lag_1", 
                   "saudi_production_roll_mean_3", "brent_price_roll_mean_3"]
        available_key_cols = [c for c in key_cols if c in df.columns]
        
        st.dataframe(df[available_key_cols].head(20), use_container_width=True)
        
        # Show full dataset info
        with st.expander("� View all feature names"):
            all_features = [c for c in df.columns if c != "date"]
            cols = st.columns(3)
            for idx, feat in enumerate(all_features):
                col_idx = idx % 3
                cols[col_idx].text(f"{idx+1}. {feat}")
        
        with st.expander("📊 View feature statistics"):
            st.dataframe(df.describe().T, use_container_width=True)


# Call the render function directly (Streamlit multipage apps execute the script)
render_features_page()
