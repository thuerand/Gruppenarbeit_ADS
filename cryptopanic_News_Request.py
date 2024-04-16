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
        
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            flattened_data = []

            for entry in data['results']:
                # Convert 'published_at' to MySQL datetime format
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
            try:
                existing_df = pd.read_csv(csv_file_path)
                updated_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates(subset=['ID_News'], keep='first')
            except FileNotFoundError:
                updated_df = new_df.drop_duplicates(subset=['ID_News'], keep='first')

            updated_df.sort_values(by='ID_News', ascending=False, inplace=True)
            updated_df.to_csv(csv_file_path, index=False)

            # Database Insertion
            try:
                connection = mysql.connector.connect(
                    host="localhost",
                    user="myuser",
                    password="mypassword",
                    database="mydatabase"
                )
                if connection.is_connected():
                    db_cursor = connection.cursor()
                    for index, row in updated_df.iterrows():
                        insert_query = """INSERT INTO crypto_news (Crypto_Code, ID_News, Kind, Positive_Votes, Negative_Votes, Important_Votes, Liked_Votes, Disliked_Votes, LOL_Votes, Toxic_Votes, Saved, Comments, published_at, Domain)
                                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                          ON DUPLICATE KEY UPDATE Positive_Votes=VALUES(Positive_Votes), Negative_Votes=VALUES(Negative_Votes), Important_Votes=VALUES(Important_Votes), Liked_Votes=VALUES(Liked_Votes), Disliked_Votes=VALUES(Disliked_Votes), LOL_Votes=VALUES(LOL_Votes), Toxic_Votes=VALUES(Toxic_Votes), Saved=VALUES(Saved), Comments=VALUES(Comments);"""
                        insert_values = (row['Crypto_Code'], row['ID_News'], row['Kind'], row['Positive_Votes'], row['Negative_Votes'], 
                                         row['Important_Votes'], row['Liked_Votes'], row['Disliked_Votes'], 
                                         row['LOL_Votes'], row['Toxic_Votes'], row['Saved'], 
                                         row['Comments'], row['published_at'], row['Domain'])
                        db_cursor.execute(insert_query, insert_values)
                        connection.commit()

            except Error as e:
                print(f"Failed to insert record into MySQL table: {e}")

            finally:
                if (connection.is_connected()):
                    db_cursor.close()
                    connection.close()

            print(f"Data for {currency} has been updated in {csv_file_path} and in the Database.")

        else:
            print(f"Error retrieving data for {currency}: {response.status_code}")

    

    central_df.to_csv(central_csv_path, index=False)
    print("Domain information from news has been updated.")

# Example usage - for testing
#fetch_cryptonews(["BTC"])
