"""
news_analysis.py

Analyzing the news to predict the future price of a cryptocurrency using votes on the news and the analysis of the news text of NLP.
Goal is the Sentiment Analysis of the news.

"""

from textblob import TextBlob

def analyze_sentiment(text):
    # Erstellen eines TextBlob-Objekts
    blob = TextBlob(text)
    
    # Erhalten des Sentiment-Wertes
    sentiment = blob.sentiment
    
    # sentiment.polarity gibt Werte von -1 bis 1, wo -1 sehr negativ und 1 sehr positiv bedeutet
    if sentiment.polarity > 0:
        return "Positiv"
    elif sentiment.polarity < 0:
        return "Negativ"
    else:
        return "Neutral"

# Beispieltexte
text1 = "Bitcoin-miners-underwater-as-production-costs-surge-post-halving"
text2 = "Bitcoin miners underwater as production costs surge post halving"

print("Text 1 Sentiment: ", analyze_sentiment(text1))
print("Text 2 Sentiment: ", analyze_sentiment(text2))
