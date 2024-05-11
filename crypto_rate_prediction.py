"""
cryptorate_predction.py

Trying to predict the future price of a cryptocurrency using votes on the news and the analysis of the news text of NLP.
"""
import os
import pandas as pd
import tensorflow as tf
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout

def create_db_connection():
    """Establish a connection to the database using SQLAlchemy."""
    try:
        engine = create_engine('mysql+mysqlconnector://myuser:mypassword@localhost/mydatabase')
        connection = engine.connect()
        print("MySQL Database connection successful via SQLAlchemy")
        return connection
    except Exception as err:
        print(f"Error: '{err}'")
        return None

def fetch_data(engine, crypto_code):
    """Fetch data from MySQL database for a specific cryptocurrency."""
    query = f"""
    SELECT d.date, d.value AS price, n.Positive_Votes, n.Negative_Votes, n.Important_Votes, n.Liked_Votes, n.Disliked_Votes, n.LOL_Votes, n.Toxic_Votes, n.Saved, n.Comments
    FROM daily_data d
    JOIN crypto_news n ON d.Crypto_Code = n.Crypto_Code AND DATE(d.date) = DATE(n.published_at)
    WHERE d.Crypto_Code = '{crypto_code}'
    ORDER BY d.date
    """
    with engine.connect() as connection:
        df = pd.read_sql(query, con=connection)
    return df

def preprocess_data(df):
    """ Prepare data for model training. """
    df['date'] = pd.to_datetime(df['date'])
    df.fillna(0, inplace=True)  # Handle missing values
    df.set_index('date', inplace=True)  # Use date as index

    # Feature and target separation
    X = df.drop('price', axis=1)
    y = df['price']

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return train_test_split(X_scaled, y, test_size=0.2, random_state=42)

def build_and_train_model(X_train, y_train, X_test, y_test):
    """ Build and train a neural network model. """
    model = Sequential([
        Dense(64, activation='relu', input_dim=X_train.shape[1]),
        Dropout(0.1),
        Dense(64, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))
    
    # Evaluate the model
    print("Model evaluation:", model.evaluate(X_test, y_test))
    return model

def predict_crypto_rate(crypto_code):
    """ Main function to predict cryptocurrency rates. """
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Workaround for TensorFlow issue with OneDNN

    engine = create_engine('mysql+mysqlconnector://myuser:mypassword@localhost/mydatabase')
    print("Attempting to connect to the database...")
    try:
        data = fetch_data(engine, crypto_code)
        X_train, X_test, y_train, y_test = preprocess_data(data)
        model = build_and_train_model(X_train, y_train, X_test, y_test)
    except Exception as e:
        print(f"Failed to process data or train model due to: {e}")

# Example usage for Bitcoin
#predict_crypto_rate('BTC')