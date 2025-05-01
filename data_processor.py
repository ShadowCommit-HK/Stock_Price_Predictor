import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_and_process_data(file_path):
    data = pd.read_csv(file_path)
    data['date'] = pd.to_datetime(data['date'])
    data = data.sort_values(['ticker', 'date'])
    data['price'] = data['original'].str.extract(r'higher at (\d+\.\d+)').astype(float)
    price_mask = data['price'].isna()
    if price_mask.any():
        alt_prices = data.loc[price_mask, 'original'].str.extract(r'dropping to (\d+\.\d+)').astype(float)
        data.loc[price_mask, 'price'] = alt_prices
    data['volume'] = data['original'].str.extract(r'volume (?:of|surging at) (\d+)').astype(float)
    data['close'] = data['price']
    for ticker in data['ticker'].unique():
        ticker_mask = data['ticker'] == ticker
        data.loc[ticker_mask, 'close'] = data.loc[ticker_mask, 'close'].fillna(method='ffill').fillna(method='bfill')
    data['daily_return'] = data.groupby('ticker')['close'].pct_change() * 100
    data['daily_return'] = data['daily_return'].fillna(0)
    sentiment_map = {'bullish': 1, 'bearish': -1, 'neutral': 0}
    data['sentiment_value'] = data['senti_label'].map(sentiment_map)
    data = data.fillna({'volume': data['volume'].median(), 'sentiment_value': 0})
    return data

def get_unique_tickers(data):
    return sorted(data['ticker'].unique())

def get_ticker_data(data, ticker):
    return data[data['ticker'] == ticker].copy()

def generate_extended_dates(last_date, days=30):
    if not isinstance(last_date, pd.Timestamp):
        last_date = pd.Timestamp(last_date)
    next_day = last_date + pd.Timedelta(days=1)
    date_range = pd.date_range(start=next_day, periods=days)
    return date_range
