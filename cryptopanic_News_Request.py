import os
import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dateutil import parser

def fetch_cryptonews(currencies):
    print("Fetching news data from cryptopanic.com...")
    folder_name = 'Data_cryptonews'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    existing_HQ_csv_path = os.path.join(folder_name, 'HQ_newsagency.csv')

    try:
        existing_HQ_df = pd.read_csv(existing_HQ_csv_path)
    except FileNotFoundError:
        existing_HQ_df = pd.DataFrame(columns=['Domain', 'hq_location'])

    base_url = "https://cryptopanic.com/api/v1/posts/?auth_token=40638bc52524aa59273d51fac8edc7d377671007&filter=hot&currencies="

    for currency in currencies:
        url = base_url + currency
        csv_file_path = os.path.join(folder_name, f'{currency}_cryptonews.csv')
        
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            flattened_data = []

            for entry in data['results']:
                published_at = parser.parse(entry['published_at']).strftime('%Y-%m-%d %H:%M:%S')
                entry_data = {
                    'ID_News': entry['id'],
                    'Crypto_Code': currency,
                    'Kind': entry['kind'],
                    'Positive_Votes': entry['votes']['positive'],
                    'Negative_Votes': entry['votes']['negative'],
                    'Important_Votes': entry['votes']['important'],
                    'Liked_Votes': entry['votes']['liked'],
                    'Disliked_Votes': entry['votes']['disliked'],
                    'LOL_Votes': entry['votes']['lol'],
                    'Toxic_Votes': entry['votes']['toxic'],
                    'Saved': entry['votes']['saved'],
                    'Comments': entry['votes']['comments'],
                    'published_at': published_at,
                    'Domain': entry['domain'],
                }
                flattened_data.append(entry_data)

            new_df = pd.DataFrame(flattened_data)
            new_HQ_df = new_df[['Domain']].drop_duplicates()

            # Check for new domains
            new_domains = new_HQ_df[~new_HQ_df['Domain'].isin(existing_HQ_df['Domain'])]
            if not new_domains.empty:
                new_domains['hq_location'] = pd.NA  # Initialize with NA
                existing_HQ_df = pd.concat([existing_HQ_df, new_domains], ignore_index=True)
                existing_HQ_df.to_csv(existing_HQ_csv_path, index=False)
                print("New domains added to HQ database.")

            try:
                existing_df = pd.read_csv(csv_file_path)
                updated_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates(subset=['ID_News'], keep='first')
            except FileNotFoundError:
                updated_df = new_df.drop_duplicates(subset=['ID_News'], keep='first')

            updated_df.sort_values(by='ID_News', ascending=False, inplace=True)
            updated_df.to_csv(csv_file_path, index=False)

            print(f"Data for {currency} has been updated in {csv_file_path}.")

        else:
            print(f"Error retrieving data for {currency}: {response.status_code}")

# Example usage - for testing
#fetch_cryptonews(["BTC"])
