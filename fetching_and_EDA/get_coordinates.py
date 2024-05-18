import requests
import mysql.connector
from mysql.connector import Error
import pandas as pd
import numpy as np
import warnings

# Ignore specific pandas UserWarning about SQLAlchemy connectable
warnings.filterwarnings('ignore', category=UserWarning,
                        message='.*pandas only supports SQLAlchemy connectable.*')

# Function to fetch coordinates from OpenCage Geocoder API


def fetch_coordinates(api_key, address):
    """Fetch coordinates from OpenCage Geocoder API."""
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": address,
        "key": api_key,
        "limit": 1
    }
    response = requests.get(base_url, params=params, timeout=10)
    data = response.json()
    if data['results']:
        latitude = data['results'][0]['geometry']['lat']
        longitude = data['results'][0]['geometry']['lng']
        return latitude, longitude
    return None, None

# Function to update the database and CSV file with coordinates


def update_database_and_csv_with_coordinates():
    csv_file_path = 'resources/data_cryptonews/HQ_newsagency.csv'
    df = pd.read_csv(csv_file_path)

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='myuser',
            password='mypassword',
            database='mydatabase'
        )
        cursor = connection.cursor()
        api_key = 'your_api_key'

        for index, row in df.iterrows():
            # Only fetch coordinates if they are NaN in the DataFrame
            if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                latitude, longitude = fetch_coordinates(api_key, row['hq_location'])
                if latitude is not None and longitude is not None:
                    df.at[index, 'latitude'] = latitude
                    df.at[index, 'longitude'] = longitude
                else:
                    df.at[index, 'latitude'] = np.nan
                    df.at[index, 'longitude'] = np.nan
                    continue  # Skip updating this row in the database if coordinates are None

            # Ensure latitude and longitude are either float or None (SQL NULL)
            latitude = float(row['latitude']) if not pd.isna(row['latitude']) else None
            longitude = float(row['longitude']) if not pd.isna(row['longitude']) else None

            # Update the database only if latitude and longitude are not None
            if latitude is not None and longitude is not None:
                update_query = """UPDATE HQ_newagency SET latitude = %s, longitude = %s WHERE Domain = %s"""
                cursor.execute(update_query, (latitude, longitude, row['Domain']))
                connection.commit()

        df.to_csv(csv_file_path, index=False)
        print("CSV file and database have been updated with new coordinates.")

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            
# Example usage
#update_database_and_csv_with_coordinates()




    

