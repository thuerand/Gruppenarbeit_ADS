"""
cryptorate_predction.py

Trying to predict the future price of a cryptocurrency using votes on the news and the analysis of the news text of NLP.
"""
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Input


def create_db_connection():
    """Establish a connection to the database using SQLAlchemy for easier query handling."""
    return create_engine('mysql+mysqlconnector://myuser:mypassword@localhost/mydatabase').connect()

def fetch_data(crypto_code):
    """Fetches hourly market data and corresponding news sentiment data for a specific cryptocurrency."""
    connection = create_db_connection()
    market_query = f"""
    SELECT timestamp, value
    FROM hourly_data
    WHERE Crypto_Code = '{crypto_code}'
    ORDER BY timestamp;
    """
    news_query = f"""
    SELECT published_at, sentiment, Positive_Votes, Negative_Votes, Important_Votes, Liked_Votes, Disliked_Votes, LOL_Votes, Toxic_Votes, Saved, Comments
    FROM crypto_news
    WHERE Crypto_Code = '{crypto_code}'
    ORDER BY published_at;
    """

    market_data = pd.read_sql(market_query, connection)
    news_data = pd.read_sql(news_query, connection)
    connection.close()

    print("Raw Data")
    print(news_data)
    
    return market_data, news_data

def preprocess_data(market_data, news_data):
    """Preprocess and combine market and news data."""
    market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])
    news_data['published_at'] = pd.to_datetime(news_data['published_at'])

    # Exponential smoothing
    alpha = 0.3  # Smoothing factor
    smoothing_columns = ['sentiment', 'Positive_Votes', 'Negative_Votes', 'Important_Votes', 'Liked_Votes', 'Disliked_Votes', 'LOL_Votes', 'Toxic_Votes', 'Saved', 'Comments']
    for column in smoothing_columns:
        news_data[column] = news_data[column].astype(float).ffill().ewm(alpha=alpha).mean()

    # Merge the data
    print("Before setting index:")
    print(news_data.head())
 
    news_data.set_index('published_at', inplace=True)

    print("After  setting index:")
    print(news_data.head())

    news_data = news_data.resample('h').ffill()

    print("After resampling and filling:")
    print(news_data.head())

    combined_data = pd.merge_asof(
        market_data.sort_values('timestamp'),
        news_data.sort_values('published_at'),
        left_on='timestamp',
        right_index=True,
        direction='forward',  # Try changing to 'forward' or 'backward' if 'nearest' doesn't work
        tolerance=pd.Timedelta('1h')  # Adjust tolerance to ensure closer matches
    )
    """
    print(combined_data.head())
    print(combined_data.tail())
    print("Market Data Sample:")
    print(market_data.head())
    print(market_data.tail())

    print("Hourly News Data Sample:")
    print(news_data.head())
    print(news_data.tail())
    """

    return combined_data

def create_features_targets(data):
    """Prepare features and targets for the model."""
    features = data[['Positive_Votes', 'Negative_Votes', 'Important_Votes', 'Liked_Votes', 'Disliked_Votes', 'LOL_Votes', 'Toxic_Votes', 'Saved', 'Comments', 'sentiment']]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    targets = data['value']
    return features_scaled, targets

def build_model():
    """ Build and return a LSTM neural network model. """
    model = Sequential([
        Input(shape=(10, 1)),  # Assuming 10 features and modifying the shape accordingly
        LSTM(50, return_sequences=True),
        Dropout(0.2),
        LSTM(50),
        Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model

def train_model(model, X_train, y_train):
    """ Reshape data and train the model """
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)  # Reshape for LSTM
    model.fit(X_train, y_train, epochs=20, batch_size=32, validation_split=0.1)

# Execution flow
crypto_code = 'BTC'  # Example for Bitcoin
market_data, news_data = fetch_data(crypto_code)
processed_data = preprocess_data(market_data, news_data)
features_scaled, targets = create_features_targets(processed_data)
model = build_model()
train_model(model, features_scaled, targets)
