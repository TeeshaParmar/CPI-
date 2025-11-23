import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="US-India CPI Comparison Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("🇺🇸 🇮🇳 US-India CPI & Currency Comparison Dashboard")
st.markdown("### Comparative Analysis for RBI Research")
st.markdown("---")

# Sidebar for data input
st.sidebar.header("Data Configuration")
data_option = st.sidebar.radio(
    "Choose data input method:",
    ["Use Sample Data", "Upload Custom Data"]
)

# Function to create sample data
def create_sample_data():
    dates = pd.date_range(start='2019-01', end='2024-10', freq='M')
    
    # Sample CPI data (Base year 2019=100)
    us_cpi_base = 100
    india_cpi_base = 100
    
    # Simulating realistic CPI trends
    us_cpi = [us_cpi_base * (1 + 0.002 * i + np.random.uniform(-0.001, 0.001)) 
              for i in range(len(dates))]
    india_cpi = [india_cpi_base * (1 + 0.004 * i + np.random.uniform(-0.002, 0.002)) 
                 for i in range(len(dates))]
    
    # Sample exchange rate (INR/USD)
    exchange_rate = [70 + i * 0.15 + np.random.uniform(-0.5, 0.5) 
                     for i in range(len(dates))]
    
    df = pd.DataFrame({
        'Date': dates,
        'US_CPI': us_cpi,
        'India_CPI': india_cpi,
        'Exchange_Rate_INR_USD': exchange_rate
    })
    
    return df

# Load or create data
if data_option == "Use Sample Data":
    df = create_sample_data()
    st.sidebar.success("✅ Sample data loaded")
else:
    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV file with columns: Date, US_CPI, India_CPI, Exchange_Rate_INR_USD",
        type=['csv']
    )
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df['Date'] = pd.to_datetime(df['Date'])
        st.sidebar.success("✅ Custom data loaded")
    else:
        st.sidebar.info("Using sample data until file is uploaded")
        df = create_sample_data()

# Date range selector
st.sidebar.markdown("---")
st.sidebar.subheader("Date Range Filter")
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()

start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

# Filter data
mask = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)
df_filtered = df[mask].copy()

# Calculate metrics
def calculate_metrics(df):
    us_inflation = ((df['US_CPI'].iloc[-1] / df['US_CPI'].iloc[0]) - 1) * 100
    india_inflation = ((df['India_CPI'].iloc[-1] / df['India_CPI'].iloc[0]) - 1) * 100
    exchange_change = ((df['Exchange_Rate_INR_USD'].iloc[-1] / df['Exchange_Rate_INR_USD'].iloc[0]) - 1) * 100
    
    return us_inflation, india_inflation, exchange_change

us_inf, india_inf, fx_change = calculate_metrics(df_filtered)

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🇺🇸 US Cumulative Inflation",
        value=f"{us_inf:.2f}%",
        delta=f"{us_inf:.2f}% change"
    )

with col2:
    st.metric(
        label="🇮🇳 India Cumulative Inflation",
        value=f"{india_inf:.2f}%",
        delta=f"{india_inf:.2f}% change"
    )

with col3:
    st.metric(
        label="💱 Exchange Rate Change",
        value=f"{fx_change:.2f}%",
        delta=f"INR {fx_change:.2f}%"
    )

with col4:
    inflation_diff = india_inf - us_inf
    st.metric(
        label="📊 Inflation Differential",
        value=f"{inflation_diff:.2f}%",
        delta="India - US"
    )

st.markdown("---")

# Tab layout for different visualizations
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 CPI Trends", 
    "💱 Exchange Rate", 
    "🔄 Comparative Analysis",
    "📊 Correlation Analysis",
    "📋 Data Table"
])

with tab1:
    st.subheader("Consumer Price Index (CPI) Trends")
    
    fig1 = go.Figure()
    
    fig1.add_trace(go.Scatter(
        x=df_filtered['Date'],
        y=df_filtered['US_CPI'],
        name='US CPI',
        line=dict(color='#0066CC', width=3),
        mode='lines+markers'
    ))
    
    fig1.add_trace(go.Scatter(
        x=df_filtered['Date'],
        y=df_filtered['India_CPI'],
        name='India CPI',
        line=dict(color='#FF9933', width=3),
        mode='lines+markers'
    ))
    
    fig1.update_layout(
        title='CPI Comparison: US vs India',
        xaxis_title='Date',
        yaxis_title='CPI (Base Year = 100)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # YoY Inflation Rate
    st.subheader("Year-over-Year Inflation Rate (%)")
    
    df_filtered['US_Inflation_YoY'] = df_filtered['US_CPI'].pct_change(12) * 100
    df_filtered['India_Inflation_YoY'] = df_filtered['India_CPI'].pct_change(12) * 100
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        x=df_filtered['Date'],
        y=df_filtered['US_Inflation_YoY'],
        name='US YoY Inflation',
        marker_color='#0066CC'
    ))
    
    fig2.add_trace(go.Bar(
        x=df_filtered['Date'],
        y=df_filtered['India_Inflation_YoY'],
        name='India YoY Inflation',
        marker_color='#FF9933'
    ))
    
    fig2.update_layout(
        title='Year-over-Year Inflation Rates',
        xaxis_title='Date',
        yaxis_title='Inflation Rate (%)',
        barmode='group',
        template='plotly_white',
        height=500
    )
    
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("INR/USD Exchange Rate Trends")
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Scatter(
        x=df_filtered['Date'],
        y=df_filtered['Exchange_Rate_INR_USD'],
        name='INR/USD',
        fill='tozeroy',
        line=dict(color='#138808', width=3),
        mode='lines'
    ))
    
    fig3.update_layout(
        title='INR/USD Exchange Rate Over Time',
        xaxis_title='Date',
        yaxis_title='Exchange Rate (INR per USD)',
        hovermode='x',
        template='plotly_white',
        height=500
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    
    # Exchange rate statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Rate", f"₹{df_filtered['Exchange_Rate_INR_USD'].mean():.2f}")
    with col2:
        st.metric("Minimum Rate", f"₹{df_filtered['Exchange_Rate_INR_USD'].min():.2f}")
    with col3:
        st.metric("Maximum Rate", f"₹{df_filtered['Exchange_Rate_INR_USD'].max():.2f}")

with tab3:
    st.subheader("Comparative Analysis: CPI vs Exchange Rate")
    
    # Normalize data for comparison
    df_filtered['US_CPI_Normalized'] = (df_filtered['US_CPI'] / df_filtered['US_CPI'].iloc[0]) * 100
    df_filtered['India_CPI_Normalized'] = (df_filtered['India_CPI'] / df_filtered['India_CPI'].iloc[0]) * 100
    df_filtered['Exchange_Rate_Normalized'] = (df_filtered['Exchange_Rate_INR_USD'] / df_filtered['Exchange_Rate_INR_USD'].iloc[0]) * 100
    
    fig4 = go.Figure()
    
    fig4.add_trace(go.Scatter(
        x=df_filtered['Date'],
        y=df_filtered['US_CPI_Normalized'],
        name='US CPI (Normalized)',
        line=dict(color='#0066CC', width=2)
    ))
    
    fig4.add_trace(go.Scatter(
        x=df_filtered['Date'],
        y=df_filtered['India_CPI_Normalized'],
        name='India CPI (Normalized)',
        line=dict(color='#FF9933', width=2)
    ))
    
    fig4.add_trace(go.Scatter(
        x=df_filtered['Date'],
        y=df_filtered['Exchange_Rate_Normalized'],
        name='Exchange Rate (Normalized)',
        line=dict(color='#138808', width=2, dash='dash')
    ))
    
    fig4.update_layout(
        title='Normalized Comparison (Base = 100)',
        xaxis_title='Date',
        yaxis_title='Index (Base Period = 100)',
        hovermode='x unified',
        template='plotly_white',
        height=500
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    
    # Purchasing Power Parity Analysis
    st.subheader("Purchasing Power Parity (PPP) Deviation")
    
    df_filtered['PPP_Implied'] = df_filtered['Exchange_Rate_INR_USD'].iloc[0] * (df_filtered['India_CPI'] / df_filtered['US_CPI']) / (df_filtered['India_CPI'].iloc[0] / df_filtered['US_CPI'].iloc[0])
    df_filtered['PPP_Deviation'] = ((df_filtered['Exchange_Rate_INR_USD'] - df_filtered['PPP_Implied']) / df_filtered['PPP_Implied']) * 100
    
    fig5 = go.Figure()
    
    fig5.add_trace(go.Scatter(
        x=df_filtered['Date'],
        y=df_filtered['Exchange_Rate_INR_USD'],
        name='Actual Exchange Rate',
        line=dict(color='#138808', width=3)
    ))
    
    fig5.add_trace(go.Scatter(
        x=df_filtered['Date'],
        y=df_filtered['PPP_Implied'],
        name='PPP Implied Rate',
        line=dict(color='#CC0000', width=3, dash='dash')
    ))
    
    fig5.update_layout(
        title='Actual vs PPP-Implied Exchange Rate',
        xaxis_title='Date',
        yaxis_title='Exchange Rate (INR/USD)',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig5, use_container_width=True)

with tab4:
    st.subheader("Correlation Analysis")
    
    # Correlation matrix
    corr_df = df_filtered[['US_CPI', 'India_CPI', 'Exchange_Rate_INR_USD']].corr()
    
    fig6 = px.imshow(
        corr_df,
        text_auto='.3f',
        color_continuous_scale='RdBu_r',
        aspect='auto',
        labels=dict(color="Correlation")
    )
    
    fig6.update_layout(
        title='Correlation Matrix: CPI and Exchange Rate',
        height=400
    )
    
    st.plotly_chart(fig6, use_container_width=True)
    
    # Scatter plot
    col1, col2 = st.columns(2)
    
    with col1:
        fig7 = px.scatter(
            df_filtered,
            x='India_CPI',
            y='Exchange_Rate_INR_USD',
            trendline='ols',
            title='India CPI vs Exchange Rate',
            labels={'India_CPI': 'India CPI', 'Exchange_Rate_INR_USD': 'INR/USD'}
        )
        st.plotly_chart(fig7, use_container_width=True)
    
    with col2:
        fig8 = px.scatter(
            df_filtered,
            x='US_CPI',
            y='Exchange_Rate_INR_USD',
            trendline='ols',
            title='US CPI vs Exchange Rate',
            labels={'US_CPI': 'US CPI', 'Exchange_Rate_INR_USD': 'INR/USD'}
        )
        st.plotly_chart(fig8, use_container_width=True)

with tab5:
    st.subheader("Raw Data Table")
    
    # Display options
    show_all = st.checkbox("Show all columns (including calculated)")
    
    if show_all:
        display_df = df_filtered
    else:
        display_df = df_filtered[['Date', 'US_CPI', 'India_CPI', 'Exchange_Rate_INR_USD']]
    
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"cpi_comparison_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
### About This Dashboard
This dashboard provides a comprehensive comparison of Consumer Price Indices (CPI) between the United States and India, 
along with exchange rate analysis. The analysis includes:
- CPI trends and year-over-year inflation rates
- Exchange rate movements (INR/USD)
- Purchasing Power Parity (PPP) analysis
- Correlation analysis between variables

**Data Sources**: Sample data is used for demonstration. Upload your own data for accurate analysis.

**Prepared for**: Reserve Bank of India (RBI) Internship Analysis
""")
