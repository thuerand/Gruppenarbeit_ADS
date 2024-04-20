import requests
import mysql.connector
from mysql.connector import Error
import pandas as pd
import numpy as np
import folium
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
    # Update both the database and CSV file with geographic coordinates."""
    csv_file_path = 'Data_cryptonews/HQ_newsagency.csv'

    df = pd.read_csv(csv_file_path)  # Load the CSV file into a DataFrame

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='myuser',
            password='mypassword',
            database='mydatabase'
        )
        cursor = connection.cursor()
        api_key = '77ace187bc104bcfa94efa947fd84326'

        # Select domains that are missing coordinates
        cursor.execute(
            "SELECT Domain, hq_location FROM HQ_newagency WHERE latitude IS NULL OR longitude IS NULL")
        rows = cursor.fetchall()

        # Mapping domains to hq_location for API calls
        domain_to_hq = {row[0]: row[1] for row in rows}

        # Iterate over DataFrame rows that need updates
        for index, row in df.iterrows():
            if row['Domain'] in domain_to_hq:
                if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                    latitude, longitude = fetch_coordinates(
                        api_key, domain_to_hq[row['Domain']])
                    if latitude is not None and longitude is not None:
                        df.at[index, 'latitude'] = latitude
                        df.at[index, 'longitude'] = longitude
                    else:
                        df.at[index, 'latitude'] = np.nan
                        df.at[index, 'longitude'] = np.nan
                        latitude, longitude = None, None  # Use None for SQL NULL

                    # Update the database
                    update_query = """UPDATE HQ_newagency SET latitude = %s, longitude = %s WHERE Domain = %s"""
                    cursor.execute(
                        update_query, (latitude, longitude, row['Domain']))
                    connection.commit()
                    print(
                        f"Updated {row['Domain']} with lat: {latitude}, lng: {longitude}")

        # Save the updated DataFrame back to the CSV
        df.to_csv(csv_file_path, index=False)
        print("CSV file has been updated with new coordinates.")

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

# Example usage
# update_database_and_csv_with_coordinates()

# Function to fetch data from the MySQL database and create an interactive map using Folium


def fetch_and_create_map():
    """Fetch data from the MySQL database and create an interactive map using Folium, grouping multiple domains at the same location."""
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host='localhost', user='myuser', password='mypassword', database='mydatabase')
        query = "SELECT Domain, hq_location, latitude, longitude FROM HQ_newagency WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
        data = pd.read_sql(query, conn)

        # Ensure the connection is closed after fetching the data
        conn.close()

        # Check if data is empty
        if data.empty:
            print("No data available to display on the map.")
            return

        # Create a map centered around the mean coordinates to ensure all points are visible
        if not data[['latitude', 'longitude']].dropna().empty:
            map_center = data[['latitude', 'longitude']].mean().tolist()
        else:
            map_center = [0, 0]  # Default to 0,0 if no valid coordinates

        map = folium.Map(location=map_center, zoom_start=2)

        # Group the data by latitude and longitude
        grouped = data.groupby(['latitude', 'longitude', 'hq_location'])

        # Add markers to the map for each group
        for (lat, lon, hq), group in grouped:
            domains_list = '<br>'.join(
                f" - {row['Domain']}" for _, row in group.iterrows())
            popup_text = f"<strong>HQ: {hq}</strong><br>Domains:<br>{domains_list}"
            popup = folium.Popup(popup_text, max_width=300)  # Set a larger width for the popup
            folium.Marker([lat, lon], popup=popup).add_to(map)

        # Save the map as an HTML file
        map.save('result/hq_locations_map.html')
        print("Map has been saved to 'hq_locations_map.html' in the 'result' folder.")

        return map

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
#fetch_and_create_map()
