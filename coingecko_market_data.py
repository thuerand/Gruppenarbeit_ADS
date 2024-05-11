""" 
coingecko_market_data.py
"""
# Fetching market data the specific cryptocurrencies from coingecko.com

import os
import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta

def fetch_and_save_crypto_hourly_data(crypto_ID, crypto_name, folder_path='data_cryptocurrency_rate'):
    # Setting start and end date for the data fetch
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    url = f"https://api.coingecko.com/api/v3/coins/{crypto_name}/market_chart/range?vs_currency=usd&from={start_timestamp}&to={end_timestamp}"

    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        prices = data.get('prices', [])

        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['Crypto_Code'] = crypto_ID

        # Round and select the nearest entries to each hour
        df['hour'] = df['timestamp'].dt.floor('h')
        df['timedelta'] = (df['timestamp'] - df['hour']).abs()
        df = df.sort_values('timedelta').groupby('hour').first().reset_index()

        # Drop unnecessary columns and round datetime to the hour
        df.drop(columns=['timedelta'], inplace=True)
        df['timestamp'] = df['hour']
        df.drop(columns=['hour'], inplace=True)

        os.makedirs(folder_path, exist_ok=True)
        csv_file_path = os.path.join(folder_path, f'{crypto_ID}_hourly_data.csv')

        # Handling the existing CSV and updating
        try:
            existing_df = pd.read_csv(csv_file_path)
            existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'])
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.drop_duplicates(subset=['timestamp'], keep='last', inplace=True)
        except FileNotFoundError:
            combined_df = df

        combined_df.sort_values(by='timestamp', ascending=False, inplace=True)
        combined_df.to_csv(csv_file_path, index=False)

        # Update MySQL database
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="myuser",
                password="mypassword",
                database="mydatabase"
            )
            if connection.is_connected():
                db_cursor = connection.cursor()
                for _, row in combined_df.iterrows():
                    insert_query = """
                        INSERT INTO hourly_data (Crypto_Code, value, timestamp)
                        VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE value = VALUES(value);
                    """
                    insert_values = (row['Crypto_Code'], float(row['price']), row['timestamp'])
                    db_cursor.execute(insert_query, insert_values)
                    connection.commit()
                print(f"Hourly data for {crypto_ID} has been updated in {csv_file_path} and in the Database.")
        except Error as e:
            print(f"Failed to insert record into MySQL table: {e}")
        finally:
            if connection.is_connected():
                db_cursor.close()
                connection.close()
    else:
        print(f"Failed to fetch data for {crypto_ID}: {response.status_code}")

# Example usage - for testing
# fetch_and_save_crypto_hourly_data("BTC", "bitcoin")