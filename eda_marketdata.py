import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import mode
from io import BytesIO
import base64

# Function to convert plot to HTML image tag
def plot_to_html_img(figure, plot_title):
    # Save plot to a bytes buffer
    buf = BytesIO()
    figure.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    # Encode the image in base64 to embed in HTML
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    # Create HTML image tag with base64 encoded image
    return f'<h2>{plot_title}</h2><img src="data:image/png;base64,{image_base64}"/>'

def fetch_and_analyze_data():
    try:
        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='myuser',
            password='mypassword',
            database='mydatabase'
        )
        # Fetch the data
        df = pd.read_sql("SELECT Crypto_Code, value AS Price, date FROM daily_data ORDER BY date", connection)
        
        if df.empty:
            return "No data available for analysis."

        # Statistics
        mean_price = df['Price'].mean()
        median_price = df['Price'].median()
        mode_price = mode(df['Price']).mode[0]

        # Create plots
        plt.figure(figsize=(10, 5))
        plt.plot(df['date'], df['Price'], label='Price')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.title('Price Trends')
        plt.legend()
        price_trend_plot = plt.gcf()  # Get the current figure

        plt.figure(figsize=(10, 5))
        plt.plot(df['date'], df['Price'].rolling(window=7).std(), label='Rolling Std Dev (7 days)', color='red')
        plt.xlabel('Date')
        plt.ylabel('Standard Deviation')
        plt.title('Price Volatility')
        plt.legend()
        volatility_plot = plt.gcf()  # Get the current figure

        # Convert plots to HTML images
        price_trend_html = plot_to_html_img(price_trend_plot, 'Price Trends Over Time')
        volatility_html = plot_to_html_img(volatility_plot, 'Price Volatility Over Time')

        # Build HTML content
        html_content = f"""
        <html>
        <head>
            <title>Crypto Market Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                img {{ display: block; margin: 20px 0; max-width: 100%; }}
            </style>
        </head>
        <body>
            <h1>Crypto Market Analysis Report</h1>
            <p><strong>Mean Price:</strong> {mean_price:.2f}</p>
            <p><strong>Median Price:</strong> {median_price:.2f}</p>
            <p><strong>Mode Price:</strong> {mode_price:.2f}</p>
            {price_trend_html}
            {volatility_html}
        </body>
        </html>
        """

        # Write the HTML content to a file
        with open('crypto_market_analysis_report.html', 'w') as file:
            file.write(html_content)

        return "Report generated successfully. Open 'crypto_market_analysis_report.html' to view it."
        
    except mysql.connector.Error as e:
        return f"Error connecting to MySQL: {e}"
    finally:
        if connection.is_connected():
            connection.close()


# result = fetch_and_analyze_data()
