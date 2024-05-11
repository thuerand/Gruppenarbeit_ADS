"""
cryptorate_predction.py

Trying to predict the future price of a cryptocurrency using votes on the news and the analysis of the news text of NLP.
"""
import os
# Set the environment variable to suppress INFO logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam


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
    
    return market_data, news_data

def preprocess_data(market_data, news_data):
    """Preprocess and combine market and news data."""
    market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])
    news_data['published_at'] = pd.to_datetime(news_data['published_at'])

    """
    Muss ausgebaut werden --> Exponential smoothing hilft nicht
    # Exponential smoothing
    alpha = 0.3  # Smoothing factor
    smoothing_columns = ['sentiment', 'Positive_Votes', 'Negative_Votes', 'Important_Votes', 'Liked_Votes', 'Disliked_Votes', 'LOL_Votes', 'Toxic_Votes', 'Saved', 'Comments']
    for column in smoothing_columns:
        news_data[column] = news_data[column].astype(float).ffill().ewm(alpha=alpha).mean()
    """
    # Merge the data
    news_data.set_index('published_at', inplace=True)


    combined_data = pd.merge_asof(
        market_data.sort_values('timestamp'),
        news_data.sort_values('published_at'),
        left_on='timestamp',
        right_index=True,
        direction='nearest',  # Try changing to 'forward' or 'backward' if 'nearest' doesn't work
        tolerance=pd.Timedelta('30m')  # Adjust tolerance to ensure closer matches
    )

    combined_data.dropna(inplace=True)  # Drop rows with NaNs
    """
    Muss ausgebaut werden --> Exponential smoothing hilft nicht
    if combined_data.isna().any().any():
        combined_data.fillna(method='ffill', inplace=True)  # forward fill to handle any remaining NaNs
        combined_data.fillna(method='bfill', inplace=True)  # forward fill to handle any remaining NaNs
    """
    print(market_data.info())
    print(news_data.info())
    print(combined_data.info())

    return combined_data

def create_features_targets(data):
    """Prepare features and targets for the model."""
    features = data[['Positive_Votes', 'Negative_Votes', 'Important_Votes', 'Liked_Votes', 'Disliked_Votes', 'LOL_Votes', 'Toxic_Votes', 'Saved', 'Comments', 'sentiment']]
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features.fillna(0))  # Fill NaNs if any left
    targets = data['value'].fillna(method='ffill')  # Ensure no NaNs in targets
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
    optimizer = Adam(learning_rate=0.001, decay=0.001/100)
    model.compile(optimizer=optimizer, loss='mean_squared_error', metrics=['mae'])
    return model

def train_model(model, X_train, y_train):
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)  # Reshape for LSTM
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.1, callbacks=[early_stopping])

# Execution flow
crypto_code = 'BTC'
market_data, news_data = fetch_data(crypto_code)
processed_data = preprocess_data(market_data, news_data)
features_scaled, targets = create_features_targets(processed_data)
model = build_model()
train_model(model, features_scaled, targets)
