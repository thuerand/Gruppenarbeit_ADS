# coingecko_market_data.py

import requests
import pandas as pd
import os
from datetime import datetime, timedelta

# Fetching market data the specific cryptocurrencies from coingecko.com
def fetch_and_save_crypto_daily_data(crypto_id, folder_path='data_cryptocurrency_rate'):
    print("Fetching daily market data from coingecko.com...")
    
    # Setting start and end date for the data fetch
    end_date = datetime.now()
    start_date = end_date - timedelta(days=15)  # Fetching data for the last 15 days due to API tier limits
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    
    url = f"https://api.coingecko.com/api/v3/coins/{crypto_id}/market_chart/range?vs_currency=usd&from={start_timestamp}&to={end_timestamp}"

    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        prices = data.get('prices', [])
        
        #Reading existing csv file
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime('%Y-%m-%d')  # Formatting directly as string in 'yyyy-mm-dd' format
        df.drop(columns=['timestamp'], inplace=True)  # Drop 'timestamp'
        df['ID_Crypto'] = crypto_id  # Assign the 3-character ID

        os.makedirs(folder_path, exist_ok=True)
        csv_file_path = os.path.join(folder_path, f'{crypto_id}_daily_data.csv')
        
        try:
            existing_df = pd.read_csv(csv_file_path)
            # Combine the new and existing data
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.drop_duplicates(subset=['date'], keep='last', inplace=True)
            if 'ID_Crypto' not in existing_df.columns:
                combined_df['ID_Crypto'] = crypto_id  # Assign the 3-character ID for existing entries without it
        except FileNotFoundError:
            combined_df = df
        
        # Ensure the order of columns as (price, date) before saving
        combined_df = combined_df[['ID_Crypto','price', 'date']]
        
        combined_df.to_csv(csv_file_path, index=False)
        print(f"Daily market data for {crypto_id} saved to {csv_file_path}")
    
    else:
        print(f"Failed to fetch data for {crypto_id}: {response.status_code}")

# Example usage - for testing
#fetch_and_save_crypto_daily_data("bitcoin")
