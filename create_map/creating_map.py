#creating_map.py

import mysql.connector
import pandas as pd
import folium

def create_map():
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
        map.save('resources/results/hq_locations_map.html')
        print("Map has been saved to 'hq_locations_map.html' in the 'resources/result' folder.")

        return map

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
#create_map()