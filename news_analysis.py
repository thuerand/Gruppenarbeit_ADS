import mysql.connector
from mysql.connector import Error
from textblob import TextBlob

def analyze_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    print(polarity)
    return polarity

def analyze_news_sentiments():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='myuser',
            password='mypassword',
            database='mydatabase'
        )
        # Using buffered cursor
        cursor = connection.cursor(buffered=True)

        select_query = "SELECT ID_News, Title FROM crypto_news WHERE sentiment IS NULL"
        cursor.execute(select_query)

        updates = []
        for (id_news, title) in cursor:
            sentiment_polarity = analyze_sentiment(title)
            updates.append((sentiment_polarity, id_news))

        # Execute updates after reading all rows
        for sentiment_polarity, id_news in updates:
            update_query = "UPDATE crypto_news SET sentiment = %s WHERE ID_News = %s"
            cursor.execute(update_query, (sentiment_polarity, id_news))

        connection.commit()
        print("Sentiment analysis complete and database updated.")
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

# Example usage - for testing
# analyze_news_sentiments()
