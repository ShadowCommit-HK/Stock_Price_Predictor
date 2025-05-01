import streamlit as st
import pandas as pd
import numpy as np
from data_processor import load_and_process_data, get_unique_tickers
from visualization import display_stock_chart, get_chart_types
from forecasting import forecast_stock_prices, get_recommendation

st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("Stock Visualization & Forecasting Dashboard")
st.markdown("""
This dashboard allows you to visualize stock data, analyze sentiment, and get forecasting insights.
""")

@st.cache_data
def load_data():
    return load_and_process_data('refined_textual_data.csv')

try:
    with st.spinner("Loading and processing stock data..."):
        data = load_data()
    
    if data is None or data.empty:
        st.error("Failed to load or process data. Please check the CSV file format.")
        st.stop()
    
    tickers = get_unique_tickers(data)
    if not tickers:
        st.error("No ticker symbols found in the data.")
        st.stop()
    
    st.sidebar.header("Dashboard Controls")
    
    selected_ticker = st.sidebar.selectbox("Select Company Ticker", tickers)
    
    st.sidebar.subheader("Forecast Settings")
    
    forecast_col1, forecast_col2 = st.sidebar.columns([2, 2])
    
    with forecast_col1:
        forecast_value = st.number_input("Forecast Period", min_value=1, max_value=100, value=1, step=1)
    
    with forecast_col2:
        forecast_unit = st.selectbox("Time Unit", options=["Days", "Months", "Years"], index=0)
    
    if forecast_unit == "Days":
        forecast_days = forecast_value
    elif forecast_unit == "Months":
        forecast_days = forecast_value * 30
    else:
        forecast_days = forecast_value * 365
    
    if forecast_unit == "Days":
        period_text = f"{forecast_value} day{'s' if forecast_value > 1 else ''}"
    elif forecast_unit == "Months":
        period_text = f"{forecast_value} month{'s' if forecast_value > 1 else ''}"
    else:
        period_text = f"{forecast_value} year{'s' if forecast_value > 1 else ''}"
        
    st.sidebar.info(f"Forecasting for {period_text} ({forecast_days} days total)")
    
    ticker_data = data[data['ticker'] == selected_ticker].copy()
    
    if not ticker_data.empty:
        col1, col2 = st.columns([7, 3])
        
        with col1:
            st.subheader(f"{selected_ticker} Stock Price Chart")
            fig = display_stock_chart(ticker_data, chart_type='line', ticker=selected_ticker)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Forecast & Recommendation")
            
            with st.spinner(f"Generating forecast for {period_text}..."):
                forecast_data = forecast_stock_prices(ticker_data, days=forecast_days)
            
            if forecast_data is not None and not forecast_data.empty:
                if 'predicted_price' in forecast_data.columns:
                    latest_price = ticker_data['close'].iloc[-1] if 'close' in ticker_data.columns else ticker_data['price'].iloc[-1]
                    forecast_price = forecast_data['predicted_price'].iloc[-1]
                    
                    if latest_price > 0:
                        price_change = ((forecast_price - latest_price) / latest_price) * 100
                    else:
                        price_change = 0
                    
                    st.metric(label="Current Price", value=f"${latest_price:.2f}")
                    st.metric(label=f"Forecasted Price ({period_text})", value=f"${forecast_price:.2f}", delta=f"{price_change:.2f}%")
                    
                    recommendation, confidence = get_recommendation(price_change)
                    
                    rec_color = {"BUY": "green", "HOLD": "blue", "SELL": "red"}
                    
                    st.markdown(f"""
                    ## Recommendation
                    <div style='background-color:{rec_color[recommendation]}; padding: 10px; border-radius: 5px; color: white; font-weight: bold; text-align: center; font-size: 24px;'>
                        {recommendation}
                    </div>
                    <p style='text-align: center; margin-top: 10px;'>Confidence: {confidence:.1f}%</p>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("Could not generate complete forecast. Showing limited information.")
            else:
                st.warning("Could not generate forecast for this stock.")
        
        if forecast_data is not None and not forecast_data.empty and 'predicted_price' in forecast_data.columns:
            st.subheader(f"Price Forecast Chart ({period_text})")
            forecast_fig = display_stock_chart(forecast_data, chart_type='line', ticker=selected_ticker, is_forecast=True)
            st.plotly_chart(forecast_fig, use_container_width=True)
        
        st.subheader("Sentiment Analysis")
        
        if 'emo_label' in ticker_data.columns and not ticker_data['emo_label'].isna().all():
            sentiment_counts = ticker_data['emo_label'].value_counts()
            
            st.subheader("Emotion Distribution")
            fig = {
                'data': [{'type': 'pie', 'labels': sentiment_counts.index, 'values': sentiment_counts.values, 'hole': 0.4, 'marker': {'colors': ['#E63946', '#457B9D', '#2A9D8F', '#F4A261', '#264653', '#E9C46A', '#9B5DE5', '#F72585', '#4CC9F0']}}],
                'layout': {'height': 400}
            }
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sentiment data available for this ticker.")
    else:
        st.error(f"No data available for {selected_ticker}")
        st.info("Please select a different ticker from the dropdown.")

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("There was a problem processing the data. Please check that the CSV file contains the expected format and columns.")
    with st.expander("Technical Error Details"):
        st.code(str(e))
        import traceback
        st.code(traceback.format_exc())