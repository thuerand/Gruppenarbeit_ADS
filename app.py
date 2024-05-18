""" 
    app.py is the main application file used to run the entire application.
    It imports necessary functions from other files and runs them in the correct order.
"""

from enviroment_setup.docker_images import run_install_Docker_images
from enviroment_setup.mySQL_setup import run_mysql_container, create_mysql_tables, wait_for_mysql_container_ready
from fetching_and_EDA.cryptopanic_News_Request import fetch_cryptonews
from fetching_and_EDA.coingecko_market_data import fetch_and_save_crypto_hourly_data
from fetching_and_EDA.similaweb_news_hq import get_hq_from_newsagencies
from fetching_and_EDA.get_coordinates import update_database_and_csv_with_coordinates
from fetching_and_EDA.eda_marketdata import analyze_and_export_data
from create_map.creating_map import create_map
from ML_Models.news_analysis import analyze_news_sentiments
from ML_Models.crypto_rate_prediction import predict_crypto_rate

print("Starting the application...")

# Define the relevant cryptocurrencies for the project (limited due to the coingecko API limit)
crypto_ids_full = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "BNB": "binancecoin",
    "SOL": "solana"
}

# Run any necessary Docker image installations first
run_install_Docker_images()

# Run the MySQL container using the Docker SDK
run_mysql_container()

# Wait for the MySQL container to be ready to accept connections
if wait_for_mysql_container_ready("localhost", "myuser", "mypassword", "mydatabase"):
    print("Proceeding with table creation and data fetching.")
    
    # Create MySQL tables
    create_mysql_tables()
    
    # Get news for each relevant coin
    fetch_cryptonews(list(crypto_ids_full.keys()))
    
    # Get rate of each relevant coin
    print("Fetching hourly market data from coingecko.com...")
    for crypto_id, crypto_name in crypto_ids_full.items():
        fetch_and_save_crypto_hourly_data(crypto_id, crypto_name)
    
    # Get HQ-location of the news agencies from data_cryptonews.csv
    get_hq_from_newsagencies()
else:
    print("Failed to connect to MySQL server after multiple attempts.")

# Get coordinates for the news agencies
update_database_and_csv_with_coordinates()

# Create an interactive map
create_map()

# EDA of marketdata
for crypto_code, crypto_name in crypto_ids_full.items():
    analyze_and_export_data(crypto_code, crypto_name)

# Get sentiment analysis of the news data
analyze_news_sentiments() # Assuming this function is defined elsewhere

# Invoke predictions after all data fetching and processing
print("Starting crypto rate predictions...")
for crypto_code, crypto_name in crypto_ids_full.items():
    predict_crypto_rate(crypto_code, crypto_name)
print("Process completed. You see the result of this Project in index.html.")