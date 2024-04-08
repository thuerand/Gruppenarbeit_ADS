# coingecko_market_data.py

import requests
import pandas as pd
import os
from datetime import datetime, timedelta

def fetch_and_save_crypto_daily_data(crypto_id, folder_path='data_cryptocurrency_rate'):
    print("Fetching daily market data from coingecko.com...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=15) #Only 15 days because of the free tier of the API
    
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart/range?vs_currency=usd&from={start_timestamp}&to={end_timestamp}"

    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        prices = data.get('prices', [])
        
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
        df.drop(columns=['timestamp'], inplace=True)
        
        os.makedirs(folder_path, exist_ok=True)
        csv_file_path = os.path.join(folder_path, f'{crypto_id}_daily_data.csv')
        
        try:
            existing_df = pd.read_csv(csv_file_path, parse_dates=['date'])
            combined_df = pd.concat([existing_df, df], ignore_index=True).drop_duplicates(subset=['date'], keep='last')
        except FileNotFoundError:
            combined_df = df
        
        combined_df.to_csv(csv_file_path, index=False, date_format='%Y-%m-%d')
        print(f"Daily market data for {crypto_id} saved to {csv_file_path}")
    else:
        print(f"Failed to fetch data for {crypto_id}: {response.status_code}")
