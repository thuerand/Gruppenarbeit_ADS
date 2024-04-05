# main.py

#Relevant cryptocurrencies for project (only 5 beacuse of the limitation of coingecko API)
crypto_ids_full = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "USDT": "tether",
    "BNB": "binancecoin",
    "SOL": "solana"
}

#Get news of each relevant coin
from cryptopanic_News_Request import fetch_cryptonews
fetch_cryptonews(list(crypto_ids_full.keys()))

#Get rate of each relevant coin
from coingecko_market_data import fetch_and_save_crypto_daily_data
for crypto_symbol, crypto_id in crypto_ids_full.items():
    fetch_and_save_crypto_daily_data(crypto_id)

#Get HQ of the newsagencys from data_cryptonews.csv
from similaweb_news_hq import get_hq_from_newsagencies