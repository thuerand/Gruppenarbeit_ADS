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

    central_csv_path = os.path.join(folder_name, 'HQ_newsagency.csv')

    try:
        central_df = pd.read_csv(central_csv_path)
    except FileNotFoundError:
        central_df = pd.DataFrame(columns=['Domain', 'hq_location'])

    base_url = "https://cryptopanic.com/api/v1/posts/?auth_token=40638bc52524aa59273d51fac8edc7d377671007&filter=hot&currencies="

    for currency in currencies:
        url = base_url + currency
        csv_file_path = os.path.join(folder_name, f'{currency}_cryptonews.csv')
        
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            flattened_data = []

            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="myuser",
                    password="mypassword",
                    database="mydatabase"
                )
                if connection.is_connected():
                    db_cursor = connection.cursor()

                    for entry in data['results']:
                        # Convert 'published_at' to MySQL datetime format
                        published_at = parser.parse(entry['published_at']).strftime('%Y-%m-%d %H:%M:%S')

                        entry_data = {
                            'ID': entry['id'],
                            'ID_Cryptopanic': currency,
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

                        # Prepare SQL insert statement
                        insert_query = """INSERT INTO crypto_news (crypto_id, ID_Cryptopanic, Kind, Positive_Votes, Negative_Votes, Important_Votes, Liked_Votes, Disliked_Votes, LOL_Votes, Toxic_Votes, Saved, Comments, published_at, Domain)
                                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                        insert_values = (currency, entry['id'], entry['kind'], entry['votes']['positive'], entry['votes']['negative'], 
                                         entry['votes']['important'], entry['votes']['liked'], entry['votes']['disliked'], 
                                         entry['votes']['lol'], entry['votes']['toxic'], entry['votes']['saved'], 
                                         entry['votes']['comments'], published_at, entry['domain'])

                        db_cursor.execute(insert_query, insert_values)
                        connection.commit()

            except Error as e:
                print(f"Failed to insert record into MySQL table: {e}")

            new_df = pd.DataFrame(flattened_data)
            try:
                existing_df = pd.read_csv(csv_file_path)
                updated_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates(subset=['ID'], keep='first')
            except FileNotFoundError:
                updated_df = new_df.drop_duplicates(subset=['ID_Cryptopanic'], keep='first')

            updated_df.sort_values(by='ID', ascending=False, inplace=True)
            updated_df.to_csv(csv_file_path, index=False)
            print(f"Data for {currency} has been updated in {csv_file_path}")

        else:
            print(f"Error retrieving data for {currency}: {response.status_code}")

    central_df.to_csv(central_csv_path, index=False)
    print("Domain information from news has been updated.")

# Example usage, with your currencies of interest:
fetch_cryptonews(["BTC"])
