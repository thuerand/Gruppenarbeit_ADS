# app.py ist the main application file, which is used to run the entire application. It imports the necessary functions from other files and runs them in the correct order. The following is the content of app.py:

# Relevant cryptocurrencies for project (only 5 beacuse of the limitation of coingecko API)
crypto_ids_full = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "BNB": "binancecoin",
    "SOL": "solana"
}

# Get the Docker thingies
from docker_images import run_install_Docker_images

# Run MySQL container using Docker SDK
from mySQL_setup import run_mysql_container

# Create mySQL tables
from mySQL_setup import create_mysql_tables

# Get news of each relevant coin
from cryptopanic_News_Request import fetch_cryptonews
fetch_cryptonews(list(crypto_ids_full.keys()))

# Get rate of each relevant coin
from coingecko_market_data import fetch_and_save_crypto_daily_data
for crypto_symbol, crypto_id in crypto_ids_full.items():
    fetch_and_save_crypto_daily_data(crypto_id)

#Get HQ of the newsagencys from data_cryptonews.csv
from similaweb_news_hq import get_hq_from_newsagencies