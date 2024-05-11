"""
cryptorate_predction.py

Trying to predict the future price of a cryptocurrency using votes on the news and the analysis of the news text of NLP.
"""
import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
from datetime import datetime, timedelta

def create_db_connection():
    """ Establish a connection to the database using SQLAlchemy for easier query handling. """
    return create_engine('mysql+mysqlconnector://myuser:mypassword@localhost/mydatabase').connect()

def fetch_data(crypto_code):
    """ Fetches hourly market data and corresponding news sentiment data for a specific cryptocurrency. """
    connection = create_db_connection()
    
    # Query to fetch hourly cryptocurrency market rates
    market_query = f"""
    SELECT timestamp, value
    FROM hourly_data
    WHERE Crypto_Code = '{crypto_code}'
    ORDER BY timestamp;
    """
    
    # Query to fetch news data
    news_query = f"""
    SELECT published_at, sentiment, Positive_Votes, Negative_Votes, Important_Votes, Liked_Votes, Disliked_Votes, LOL_Votes, Toxic_Votes, Saved, Comments
    FROM crypto_news
    WHERE Crypto_Code = '{crypto_code}'
    ORDER BY published_at;
    """
    
    # Read the data into Pandas DataFrames
    market_data = pd.read_sql(market_query, connection)
    news_data = pd.read_sql(news_query, connection)
    
    # Close the database connection
    connection.close()
    
    return market_data, news_data

def preprocess_data(market_data, news_data):
    """ Preprocess and combine market and news data. """
    # Convert timestamps to datetime objects and set as index
    market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])
    news_data['published_at'] = pd.to_datetime(news_data['published_at'])
    
    # Resample news data to hourly and forward fill to align with market data
    news_data.set_index('published_at', inplace=True)
    hourly_news = news_data.resample('H').ffill()
    
    # Merge datasets on the timestamp
    combined_data = pd.merge_asof(market_data.sort_values('timestamp'), hourly_news.sort_values('published_at'), left_on='timestamp', right_index=True, direction='nearest')
    
    return combined_data

def build_model():
    """ Build and return a simple LSTM model for time series prediction. """
    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(1, 10)),  # Assuming 10 input features
        Dropout(0.2),
        LSTM(50),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_model(model, X_train, y_train):
    """ Train the model on the data. """
    model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.1)

# Main Execution
crypto_code = 'BTC'  # Example for Bitcoin
market_data, news_data = fetch_data(crypto_code)
processed_data = preprocess_data(market_data, news_data)

# Assume some function to create features and targets from processed_data
X_train, y_train = create_features_targets(processed_data)

model = build_model()
train_model(model, X_train, y_train)
