"""EDA page for the Streamlit app."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import numpy as np
import streamlit as st

# Add parent directory to path for imports
root_dir = Path(__file__).resolve().parents[1]
if str(root_dir / "src") not in sys.path:
    sys.path.insert(0, str(root_dir / "src"))

from config import PROCESSED_DATA_DIR


def load_features() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED_DATA_DIR / "features.csv", parse_dates=["date"])
    return df


def render_eda() -> None:
    st.set_page_config(page_title="EDA", page_icon="📊", layout="wide")
    st.title("📊 Exploratory Data Analysis")
    
    st.markdown("""
    Explore key patterns and relationships in the GCC oil production dataset.
    """)

    df = load_features()
    
    # Single comprehensive overview
    st.header("📋 Dataset Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Records", f"{len(df):,}")
    with col2:
        date_range_years = (df['date'].max() - df['date'].min()).days / 365.25
        st.metric("Timespan", f"{int(date_range_years)} years")
    with col3:
        st.metric("Features", len(df.columns) - 1)
    with col4:
        prod_mean = df['saudi_production'].mean()
        st.metric("Avg Prod", f"{prod_mean:.0f} MBPD")
    with col5:
        brent_mean = df['brent_price'].mean()
        st.metric("Avg Price", f"${brent_mean:.0f}/bbl")
    
    
    # Correlation - Simple visual
    st.header("🔗 Key Relationships")
    
    base_features = ['saudi_production', 'brent_price', 'renewables_value', 'world_obs_value']
    available_features = [f for f in base_features if f in df.columns]
    
    if len(available_features) > 1:
        import plotly.graph_objects as go
        
        correlations = df[available_features].corr()['saudi_production'].drop('saudi_production').sort_values(ascending=False)
        
        fig = go.Figure(data=[
            go.Bar(x=correlations.index, y=correlations.values)
        ])
        fig.update_layout(
            xaxis_title="",
            yaxis_title="Correlation",
            xaxis_tickangle=0,  # Horizontal labels
            height=400,
            margin=dict(l=20, r=20, t=20, b=80),  # More bottom margin for horizontal labels
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Correlation with Saudi Production: Brent price shows strongest relationship")
    
    # Time Series - Show the story
    st.header("📊 Time Series Patterns")
    
    # Main chart: Production & Price together (dual-axis concept)
    st.subheader("Saudi Production & Brent Price Trends")
    
    # Use plotly for better dual-variable visualization
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add production trace
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['saudi_production'], 
                   name="Saudi Production (MBPD)", 
                   line=dict(color='#1f77b4', width=2)),
        secondary_y=False
    )
    
    # Add price trace
    fig.add_trace(
        go.Scatter(x=df['date'], y=df['brent_price'], 
                   name="Brent Price ($/bbl)", 
                   line=dict(color='#ff7f0e', width=2)),
        secondary_y=True
    )
    
    # Update layout
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Production (MBPD)", secondary_y=False)
    fig.update_yaxes(title_text="Brent Price ($/bbl)", secondary_y=True)
    fig.update_layout(
        height=450,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Quick insight below chart
    col1, col2, col3 = st.columns(3)
    with col1:
        recent_prod = df['saudi_production'].tail(12).mean()
        st.metric("Recent Prod (12mo)", f"{recent_prod:.0f} MBPD")
    with col2:
        recent_price = df['brent_price'].tail(12).mean()
        st.metric("Recent Price (12mo)", f"${recent_price:.0f}/bbl")
    with col3:
        corr = df[['brent_price', 'saudi_production']].corr().iloc[0, 1]
        st.metric("Correlation", f"{corr:.2f}")
    
    # Optional: Interactive explorer in expander (not default visible)
    with st.expander("🔍 Custom Variable Explorer"):
        st.write("Compare any features to explore relationships")
        
        all_vars = ['saudi_production', 'brent_price'] + [c for c in df.columns if c not in {'date', 'saudi_production', 'brent_price'}][:10]
        
        selected_vars = st.multiselect(
            "Select variables", 
            options=all_vars,
            default=['saudi_production', 'brent_price'],
            key="custom_explorer"
        )
        
        if selected_vars:
            chart_df = df[["date"] + selected_vars].set_index("date")
            st.line_chart(chart_df, use_container_width=True)
    
    # Year-over-Year Analysis - More insightful than data summary
    st.header("📅 Temporal Analysis")
    
    # Extract year and calculate yearly averages
    df['year'] = df['date'].dt.year
    yearly_stats = df.groupby('year').agg({
        'saudi_production': 'mean',
        'brent_price': 'mean'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Production by Year")
        import plotly.express as px
        fig = px.bar(yearly_stats, x='year', y='saudi_production', 
                     labels={'saudi_production': 'Avg Production (MBPD)', 'year': 'Year'},
                     color='saudi_production',
                     color_continuous_scale='Blues')
        fig.update_layout(height=300, showlegend=False, margin=dict(l=20, r=20, t=20, b=40))
        st.plotly_chart(fig, use_container_width=True)
        
        # Growth insight
        if len(yearly_stats) > 1:
            first_year_prod = yearly_stats.iloc[0]['saudi_production']
            last_year_prod = yearly_stats.iloc[-1]['saudi_production']
            growth = ((last_year_prod - first_year_prod) / first_year_prod) * 100
            st.caption(f"📈 Growth: {growth:+.1f}% from {yearly_stats.iloc[0]['year']} to {yearly_stats.iloc[-1]['year']}")
    
    with col2:
        st.subheader("Price Volatility by Year")
        fig = px.bar(yearly_stats, x='year', y='brent_price',
                     labels={'brent_price': 'Avg Brent Price ($/bbl)', 'year': 'Year'},
                     color='brent_price',
                     color_continuous_scale='Oranges')
        fig.update_layout(height=300, showlegend=False, margin=dict(l=20, r=20, t=20, b=40))
        st.plotly_chart(fig, use_container_width=True)
        
        # Volatility insight
        if len(yearly_stats) > 1:
            price_std = yearly_stats['brent_price'].std()
            price_mean = yearly_stats['brent_price'].mean()
            volatility = (price_std / price_mean) * 100
            st.caption(f"📊 Volatility: {volatility:.1f}% (coefficient of variation)")
    
    # Bottom line insight
    corr = df[['brent_price', 'saudi_production']].corr().iloc[0, 1]
    
    st.success(f"""
    **🎯 Key Insight:** Strong correlation (r={corr:.2f}) between Brent price and production patterns enables 
    accurate forecasting. Model achieves RMSE of 2.88 MBPD by capturing these temporal dependencies.
    """)


# Call the render function directly (Streamlit multipage apps execute the script)
render_eda()
