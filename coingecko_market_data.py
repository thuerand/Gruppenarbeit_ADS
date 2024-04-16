""" 
coingecko_market_data.py
"""

import os
from datetime import datetime, timedelta
import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error

# Fetching market data the specific cryptocurrencies from coingecko.com


def fetch_and_save_crypto_daily_data(crypto_ID, crypto_name, folder_path='data_cryptocurrency_rate'):

    # Setting start and end date for the data fetch
    end_date = datetime.now()
    # Fetching data for the last 15 days due to API tier limits
    start_date = end_date - timedelta(days=15)
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    url = f"https://api.coingecko.com/api/v3/coins/{crypto_name}/market_chart/range?vs_currency=usd&from={start_timestamp}&to={end_timestamp}"

    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        prices = data.get('prices', [])

        # Reading existing csv file
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.strftime(
            '%Y-%m-%d')  # Formatting directly as string in 'yyyy-mm-dd' format
        df.drop(columns=['timestamp'], inplace=True)  # Drop 'timestamp'
        df['Crypto_Code'] = crypto_ID  # Assign the 3-character ID

        os.makedirs(folder_path, exist_ok=True)
        csv_file_path = os.path.join(
            folder_path, f'{crypto_ID}_daily_data.csv')

        try:
            existing_df = pd.read_csv(csv_file_path)
            # Combine the new and existing data
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.drop_duplicates(
                subset=['date'], keep='last', inplace=True)
            if 'Crypto_Code' not in existing_df.columns:
                # Assign the 3-character ID for existing entries without it
                combined_df['Crypto_Code'] = crypto_ID
        except FileNotFoundError:
            combined_df = df

        # Ensure the order of columns as (price, date) before saving
        combined_df = combined_df[['Crypto_Code', 'price', 'date']]

        combined_df.to_csv(csv_file_path, index=False)

        # Attempt to connect to your MySQL database
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="myuser",
                password="mypassword",
                database="mydatabase"
            )

            if connection.is_connected():
                db_cursor = connection.cursor()

                # Iterate through the DataFrame rows
                for _, row in combined_df.iterrows():
                    insert_query = """INSERT INTO daily_data (Crypto_Code, value, date)
                                      VALUES (%s, %s, %s)
                                      ON DUPLICATE KEY UPDATE value = VALUES(value);"""
                    insert_values = (row['Crypto_Code'],
                                     row['price'], row['date'])

                    db_cursor.execute(insert_query, insert_values)
                    connection.commit()

            print(
                f"Data for {crypto_ID} has been updated in {csv_file_path} and in the Database.")

        except Error as e:
            print(f"Failed to insert record into MySQL table: {e}")

        finally:
            if (connection.is_connected()):
                db_cursor.close()
                connection.close()

    else:
        print(f"Failed to fetch data for {crypto_ID}: {response.status_code}")
# Example usage - for testing
# fetch_and_save_crypto_daily_data("BTC", "bitcoin")
