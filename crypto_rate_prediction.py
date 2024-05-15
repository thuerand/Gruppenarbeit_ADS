import os
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64

def create_db_connection():
    """Establish a connection to the database using SQLAlchemy."""
    return create_engine('mysql+mysqlconnector://myuser:mypassword@localhost/mydatabase').connect()

def fetch_data(crypto_code):
    connection = create_db_connection()
    market_query = f"SELECT timestamp, value FROM hourly_data WHERE Crypto_Code = '{crypto_code}' ORDER BY timestamp DESC LIMIT 960;"  # Last 40 days assuming 24 readings per day
    news_query = f"SELECT published_at, sentiment, Positive_Votes, Negative_Votes, Important_Votes, Liked_Votes, Disliked_Votes, LOL_Votes, Toxic_Votes, Saved, Comments FROM crypto_news WHERE Crypto_Code = '{crypto_code}' ORDER BY published_at DESC LIMIT 960;"
    market_data = pd.read_sql(market_query, connection)
    news_data = pd.read_sql(news_query, connection)
    connection.close()
    return market_data, news_data

def preprocess_data(market_data, news_data):
    market_data['timestamp'] = pd.to_datetime(market_data['timestamp'])
    news_data['published_at'] = pd.to_datetime(news_data['published_at'])
    news_data.set_index('published_at', inplace=True)
    news_data = news_data.resample('h').ffill()
    combined_data = pd.merge_asof(market_data.sort_values('timestamp'), news_data.sort_values('published_at'), left_on='timestamp', right_index=True, direction='nearest', tolerance=pd.Timedelta('1h'))
    combined_data.dropna(inplace=True)
    return combined_data

def create_features_targets(data, forecast_hours=167):
    """Prepare features and targets for the model."""
    data = data.sort_values('timestamp')
    features = data[['Positive_Votes', 'Negative_Votes', 'Important_Votes', 'Liked_Votes', 'Disliked_Votes', 'LOL_Votes', 'Toxic_Votes', 'Saved', 'Comments', 'sentiment']]
    
    # Create lagged features efficiently
    lags = {f'lag_{i}': data['value'].shift(-i) for i in range(1, forecast_hours + 1)}
    lag_df = pd.DataFrame(lags)
    
    # Join lagged features to the main DataFrame
    data = pd.concat([data, lag_df], axis=1)
    
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    targets = data[[f'lag_{i}' for i in range(1, forecast_hours + 1)]].values
    
    # Exclude the last n rows for which we cannot create future targets
    valid_indices = ~np.isnan(targets).any(axis=1)
    return features_scaled[valid_indices], targets[valid_indices]

def build_and_train_model(features, targets, crypto_code,n_estimators=100):
    X_train, X_test, y_train, y_test = train_test_split(features, targets, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=100)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    rmse = mse ** 0.5  # Taking the square root manually
    print(f"RMSE for {crypto_code}: {rmse}")
    return model, X_test, y_test, predictions

def plot_predictions(data, predictions, crypto_name):
    """ Plot historical data and future predictions with a continuous line """
    plt.figure(figsize=(12, 6))
    
    # Plotting historical data
    plt.plot(data['timestamp'], data['value'], label='Historical Daily Values', color='blue')

    # Generate future timestamps starting right after the last historical timestamp
    last_timestamp = data['timestamp'].iloc[-1]
    future_timestamps = [last_timestamp + pd.Timedelta(hours=i) for i in range(1, len(predictions[-1]) + 1)]

    # Adjust predictions to start from the last historical data point
    full_predictions = np.concatenate(([data['value'].iloc[-1]], predictions[-1]))

    # Plotting predicted values
    plt.plot([last_timestamp] + future_timestamps, full_predictions, 'r-', label='Forecasted Values')
    
    plt.title(f'Historical and Forecasted Prices for {crypto_name}')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True)

    # Save plot to buffer for HTML conversion
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    
    return f'<img src="data:image/png;base64,{image_base64}" alt="Historical and Predicted Prices"/>'


# Execution flow
crypto_code = 'BTC'  # Example for Bitcoin
market_data, news_data = fetch_data(crypto_code)
processed_data = preprocess_data(market_data, news_data)
features_scaled, targets_future = create_features_targets(processed_data)
model, X_test, y_test, predictions = build_and_train_model(features_scaled, targets_future, crypto_code)
prediction_plot_html = plot_predictions(processed_data, predictions, crypto_code)

# Save the plot to HTML
html_content = f"""
<html>
<head>
    <title>{crypto_code} Price Forecast</title>
</head>
<body>
    <h1>Price Forecast for {crypto_code}</h1>
    {prediction_plot_html}
</body>
</html>
"""
html_file_path = f"results/prediction_results_{crypto_code}.html"
with open(html_file_path, 'w') as file:
    file.write(html_content)
print(f"Results saved to {html_file_path}")
