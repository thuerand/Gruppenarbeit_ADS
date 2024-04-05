# cryptopanic_News_Request.py

import os
import requests
import pandas as pd

def fetch_cryptonews(currencies):
    folder_name = 'Data_cryptonews'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Path to the central CSV file for domain management
    central_csv_path = os.path.join(folder_name, 'HQ_newsagency.csv')
    
    # Try to read the central CSV file or create an empty DataFrame if it doesn't exist
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

                # Add domain to central_df if not already present
                if entry['domain'] not in central_df['Domain'].values:
                    # Prepare the new row as a DataFrame
                    new_row_df = pd.DataFrame([{'Domain': entry['domain'], 'hq_location': pd.NA}])
                    
                    # Concatenate the new row DataFrame with the central DataFrame
                    central_df = pd.concat([central_df, new_row_df], ignore_index=True)

            new_df = pd.DataFrame(flattened_data)
            try:
                existing_df = pd.read_csv(csv_file_path)
                updated_df = pd.concat([existing_df, new_df], ignore_index=True).drop_duplicates(subset=['ID'], keep='first')
            except FileNotFoundError:
                updated_df = new_df.drop_duplicates(subset=['ID'], keep='first')

            # Sort the DataFrame in descending order by 'ID'
            updated_df.sort_values(by='ID', ascending=False, inplace=True)

            updated_df.to_csv(csv_file_path, index=False)
            print(f"Data for {currency} has been updated in {csv_file_path}")

        else:
            print(f"Error retrieving data for {currency}: {response.status_code}")

    # Save the updated central domain information
    central_df.to_csv(central_csv_path, index=False)
    print("Central domain information has been updated.")
