📈 Stock Visualization & Forecasting Dashboard
This is an interactive Streamlit-based dashboard that enables users to visualize historical stock trends, analyze sentiment from textual data, and forecast future stock prices using machine learning models.

🔧 Features
📊 Stock Chart Visualization with sentiment markers.
🤖 Sentiment Analysis from textual data (with emojis).
📉 Price Forecasting using Prophet or fallback trend-based logic.
💡 Buy/Hold/Sell Recommendations based on forecasted price changes.
⏳ Custom Forecast Period selection in Days/Months/Years.

📁 File Structure
   .
├── app.py                     # Streamlit frontend and control logic
├── data_processor.py         # Data loading, cleaning, and transformation
├── forecasting.py            # Forecasting model and recommendation logic
├── visualization.py          # Plotly-based chart rendering
├── refined_textual_data.csv  # Processed stock sentiment dataset

Prerequisites
Install the required Python packages:
  pip install -r requirements.txt
If requirements.txt is not available, install manually:
  pip install streamlit pandas numpy plotly prophet

Running the App 
  streamlit run app.py
How It Works
 The app reads stock and sentiment data from refined_textual_data.csv.
 Users select a stock ticker and forecast period via sidebar controls.
 Price data is visualized with sentiment emojis (e.g., 😊, 😟).
 The app uses Prophet (or a fallback model) to forecast future prices.
 Based on the predicted trend, a recommendation (BUY/HOLD/SELL) is displayed.

Example Insights
 Forecast: "AAPL stock may increase by 6.3% in the next 3 months."
 Recommendation: "BUY with 56% confidence"
 Sentiment: Majority emotion is "confident" 😊

Notes
 The app handles missing price/sentiment data gracefully using regex extraction and smoothing.
 When Prophet fails or data is insufficient, the fallback model ensures forecasting continuity.
 Emotion labels must be precomputed in the CSV (emo_label column).  

Author
Harsh Kumar Singh — AI & Data Science Enthusiast
