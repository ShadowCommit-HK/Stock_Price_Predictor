import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from prophet import Prophet
import warnings

warnings.filterwarnings("ignore")

def forecast_stock_prices(data, days=30):
    try:
        df = data.copy().sort_values('date')
        price_series = df['close'].values
        price_series = np.nan_to_num(price_series, nan=np.nanmean(price_series))
        last_price = price_series[-1]

        if len(price_series) < 10:
            forecast_values = []
            recent_trend = (price_series[-1] - price_series[-3]) / price_series[-3] if len(price_series) >= 3 else 0.002
            trend_factor = min(1.0, days / 30) * (1 + days / 100)
            current_price = last_price
            for i in range(days):
                day_factor = (i + 1) / days
                trend_influence = recent_trend * (1 + day_factor * trend_factor)
                volatility = last_price * 0.005 * (1 + day_factor * 2)
                daily_change = current_price * trend_influence + np.random.normal(0, volatility)
                current_price = max(0.01, current_price + daily_change)
                forecast_values.append(current_price)
            forecast_values = np.array(forecast_values)
        else:
            try:
                # Prepare data for Prophet
                prophet_df = df[['date', 'close']].rename(columns={'date': 'ds', 'close': 'y'})
                model = Prophet()
                model.fit(prophet_df)
                future = model.make_future_dataframe(periods=days)
                forecast = model.predict(future)
                forecast_values = forecast['yhat'][-days:].values

                if days > 30:
                    hist_volatility = np.std(price_series[-30:]) if len(price_series) >= 30 else np.std(price_series)
                    volatility_factors = np.linspace(1.0, 1.0 + (days/100), days)
                    for i in range(days):
                        day_factor = (i + 1) / days
                        noise = np.random.normal(0, hist_volatility * volatility_factors[i] * day_factor)
                        forecast_values[i] += noise
                    forecast_values = np.maximum(forecast_values, last_price * 0.5)
            except Exception as e:
                print(f"Prophet model failed: {str(e)}. Using enhanced trend model.")
                if len(price_series) >= 30:
                    short_trend = (price_series[-1] - price_series[-10]) / (price_series[-10] * 10)
                    medium_trend = (price_series[-1] - price_series[-30]) / (price_series[-30] * 30)
                    daily_change = short_trend * 0.3 + medium_trend * 0.7 if days > 30 else short_trend
                else:
                    daily_change = np.diff(price_series).mean()
                forecast_values = []
                current_price = last_price
                for i in range(days):
                    time_factor = 1.0 + (i / days)
                    volatility = abs(daily_change) * (1 + i/10) * 0.5
                    random_component = np.random.normal(0, volatility)
                    change = (daily_change * time_factor) + random_component
                    current_price = max(0.01, current_price + change)
                    forecast_values.append(current_price)
                forecast_values = np.array(forecast_values)

        # Apply smoothing to the forecast values
        forecast_values = pd.Series(forecast_values).rolling(window=3, min_periods=1).mean().values

        last_date = df['date'].max()
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)
        forecast_df = pd.DataFrame({'date': forecast_dates, 'close': forecast_values, 'predicted_price': forecast_values, 'forecast': True})
        historical_df = df[['date', 'close']].copy()
        historical_df['predicted_price'] = historical_df['close']
        historical_df['forecast'] = False
        combined_df = pd.concat([historical_df, forecast_df], ignore_index=True)
        return combined_df
    except Exception as e:
        print(f"Error in forecasting: {str(e)}")
        df = data.copy()
        last_price = df['close'].iloc[-1] if not df.empty else 100.0
        last_date = df['date'].max() if not df.empty else datetime.now()
        last_date_ts = pd.Timestamp(last_date) if not isinstance(last_date, pd.Timestamp) else last_date
        forecast_dates = pd.date_range(start=last_date_ts + pd.Timedelta(days=1), periods=days)
        forecast_values = []
        current_price = last_price
        trend_bias = 0.001
        volatility = last_price * 0.01
        for i in range(days):
            day_volatility = volatility * (1 + i/days)
            daily_change = current_price * trend_bias + np.random.normal(0, day_volatility)
            current_price = max(0.01, current_price + daily_change)
            forecast_values.append(current_price)

        # Apply smoothing to the forecast values
        forecast_values = pd.Series(forecast_values).rolling(window=3, min_periods=1).mean().values

        forecast_df = pd.DataFrame({'date': forecast_dates, 'close': forecast_values, 'predicted_price': forecast_values, 'forecast': True})
        historical_df = df[['date', 'close']].copy() if not df.empty else pd.DataFrame({'date': [last_date], 'close': [last_price]})
        historical_df['predicted_price'] = historical_df['close']
        historical_df['forecast'] = False
        return pd.concat([historical_df, forecast_df], ignore_index=True)

def get_recommendation(price_change):
    if price_change > 5:
        confidence = min(100, 50 + price_change)
        return "BUY", confidence
    elif price_change < -5:
        confidence = min(100, 50 + abs(price_change))
        return "SELL", confidence
    else:
        confidence = max(0, 50 - abs(price_change) * 5)
        return "HOLD", confidence
