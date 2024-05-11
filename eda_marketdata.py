import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mode
from io import BytesIO
import base64
import os

def plot_to_html_img(figure, plot_title):
    """Converts a matplotlib figure to an HTML image."""
    buf = BytesIO()
    figure.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return f'<h2>{plot_title}</h2><img src="data:image/png;base64,{image_base64}"/>'

def analyze_and_export_data(crypto_code, crypto_name):
    """Fetches the market data for a given cryptocurrency, analyzes it, and exports the analysis to an HTML file."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='myuser',
            password='mypassword',
            database='mydatabase'
        )

        # Fetch the data specific to the cryptocurrency
        query = f"SELECT value AS Price, Timestamp FROM hourly_data WHERE Crypto_Code = '{crypto_code}' ORDER BY timestamp"
        df = pd.read_sql(query, connection)
        connection.close()

        if df.empty:
            print(f"No data available for {crypto_name}.")
            return

        # Calculate statistics
        mean_price = df['Price'].mean()
        median_price = df['Price'].median()

        # Create a plot for price trends
        plt.figure(figsize=(10, 5))
        plt.plot(df['Timestamp'], df['Price'], label='Price', color='blue')
        plt.title(f'Price Trends for {crypto_name}')
        plt.xlabel('Timestamp')
        plt.ylabel('Price (USD)')
        plt.grid(True)
        plt.legend()
        price_trend_plot = plt.gcf()
        plt.close()

        # Create a plot for rolling standard deviation to show volatility
        plt.figure(figsize=(10, 5))
        plt.plot(df['Timestamp'], df['Price'].rolling(window=7).std(), label='Rolling Std Dev (7 days)', color='red')
        plt.title(f'Price Volatility for {crypto_name}')
        plt.xlabel('Timestamp')
        plt.ylabel('Standard Deviation')
        plt.grid(True)
        plt.legend()
        volatility_plot = plt.gcf()
        plt.close()

        # Convert plots to HTML images
        price_trend_html = plot_to_html_img(price_trend_plot, 'Price Trends Over Time')
        volatility_html = plot_to_html_img(volatility_plot, 'Price Volatility Over Time')

        # Build HTML content
        html_content = f"""
        <html>
        <head>
            <title>{crypto_name} Market Analysis</title>
            <style>
                body {{ font-family: Arial; }}
                img {{ width: 50%; height: auto; }}
            </style>
        </head>
        <body>
            <h1>Market Analysis for {crypto_name}</h1>
            <p><strong>Mean Price:</strong> {mean_price:.2f}</p>
            <p><strong>Median Price:</strong> {median_price:.2f}</p>
            {price_trend_html}
            {volatility_html}
        </body>
        </html>
        """

        # Ensure the results directory exists
        results_dir = 'results'
        os.makedirs(results_dir, exist_ok=True)

        # Save HTML to a file
        file_path = os.path.join(results_dir, f"{crypto_code}_analysis.html")
        with open(file_path, 'w') as file:
            file.write(html_content)

        print(f"Analysis for {crypto_name} saved in the 'results' folder")

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL for {crypto_name}: {e}")

# This function can now be called from app.py to analyze and export data for each cryptocurrency in your list.
