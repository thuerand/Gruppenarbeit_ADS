# cryptopanic_News_Request.py

import os
import requests
import pandas as pd

def fetch_cryptonews(currencies):
    # Create the subfolder if it doesn't exist
    folder_name = 'Data_cryptonews'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Setup the base URL and API token
    base_url = "https://cryptopanic.com/api/v1/posts/?auth_token=40638bc52524aa59273d51fac8edc7d377671007&filter=hot&currencies="

    for currency in currencies:
        # Update the URL for the current currency
        url = base_url + currency
        
        # Setup CSV file name based on the currency, saved in the specified folder
        csv_file_path = os.path.join(folder_name, f'{currency}_cryptonews.csv')
        
        # Get data from the API
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()

            # Initialize an empty list for flattened data
            flattened_data = []

            # Process each entry in 'results'
            for entry in data['results']:
                entry_data = {
                    'ID': entry['id'],
                    'Kind': entry['kind'],
                    'Positive Votes': entry['votes']['positive'],
                    'Negative Votes': entry['votes']['negative'],
                    'Important Votes': entry['votes']['important'],
                    'Liked Votes': entry['votes']['liked'],
                    'Disliked Votes': entry['votes']['disliked'],
                    'LOL Votes': entry['votes']['lol'],
                    'Toxic Votes': entry['votes']['toxic'],
                    'Saved': entry['votes']['saved'],
                    'Comments': entry['votes']['comments'],
                    'published_at': entry['published_at'],
                    'Domain': entry['domain'],
                }
                flattened_data.append(entry_data)

            # Create DataFrame from flattened data
            new_df = pd.DataFrame(flattened_data)

            # Combine new data with existing data, if any, and remove duplicates
            try:
                existing_df = pd.read_csv(csv_file_path)
                updated_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates(subset=['ID'], keep='first')
            except FileNotFoundError:
                updated_df = new_df.drop_duplicates(subset=['ID'], keep='first')

            # Overwrite the corresponding CSV file with the updated DataFrame
            updated_df.to_csv(csv_file_path, index=False)

            print(f"Data for {currency} has been updated in {csv_file_path}")

        else:
            print(f"Error retrieving data for {currency}: {response.status_code}")
