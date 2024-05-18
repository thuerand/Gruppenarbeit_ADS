import os
import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dateutil import parser

def fetch_cryptonews(currencies):
    print("Fetching news data from cryptopanic.com...")
    folder_name = 'resources/data_cryptonews'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    existing_HQ_csv_path = os.path.join(folder_name, 'HQ_newsagency.csv')

    try:
        existing_HQ_df = pd.read_csv(existing_HQ_csv_path)
    except FileNotFoundError:
        existing_HQ_df = pd.DataFrame(columns=['Domain', 'hq_location'])

    base_url = "https://cryptopanic.com/api/v1/posts/?auth_token=40638bc52524aa59273d51fac8edc7d377671007&filter=hot&currencies="
    
    connection = mysql.connector.connect(
        host='localhost',
        user='myuser',
        password='mypassword',
        database='mydatabase'
    )
    cursor = connection.cursor()

    for currency in currencies:
        url = base_url + currency
        csv_file_path = os.path.join(folder_name, f'{currency}_cryptonews.csv')
        
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            flattened_data = []

            for entry in data['results']:
                published_at = parser.parse(entry['published_at']).strftime('%Y-%m-%d %H:%M:%S')
                entry_data = (
                    entry['id'],
                    currency,
                    entry['kind'],
                    entry['title'],
                    entry['votes']['positive'],
                    entry['votes']['negative'],
                    entry['votes']['important'],
                    entry['votes']['liked'],
                    entry['votes']['disliked'],
                    entry['votes']['lol'],
                    entry['votes']['toxic'],
                    entry['votes']['saved'],
                    entry['votes']['comments'],
                    published_at,
                    entry['domain'],
                )
                
                flattened_data.append(entry_data)

            new_df = pd.DataFrame(flattened_data, columns=['ID_News', 'Crypto_Code', 'Kind', 'Title', 'Positive_Votes', 'Negative_Votes', 'Important_Votes', 'Liked_Votes', 'Disliked_Votes', 'LOL_Votes', 'Toxic_Votes', 'Saved', 'Comments', 'published_at', 'Domain'])

            try:
                existing_df = pd.read_csv(csv_file_path)
                updated_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates(subset=['ID_News'], keep='last')
            except FileNotFoundError:
                updated_df = new_df.drop_duplicates(subset=['ID_News'], keep='first')

            updated_df.sort_values(by='ID_News', ascending=False, inplace=True)
            updated_df.to_csv(csv_file_path, index=False)

            # Insert each row into the database
            insert_query = """
            INSERT IGNORE INTO crypto_news
            (ID_News, Crypto_Code, Kind, Title, Positive_Votes, Negative_Votes, Important_Votes, Liked_Votes, Disliked_Votes, LOL_Votes, Toxic_Votes, Saved, Comments, published_at, Domain)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            for index, row in updated_df.iterrows():
                cursor.execute(insert_query, tuple(row))

            connection.commit()
            print(f"Data for {currency} has been updated in {csv_file_path} and database.")
        else:
            print(f"Error retrieving data for {currency}: {response.status_code}")

    cursor.close()
    connection.close()

# Example usage - for testing
# fetch_cryptonews(["BTC"])