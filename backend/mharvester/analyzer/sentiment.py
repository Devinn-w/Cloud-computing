from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import math

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> float:
    try:
        score = analyzer.polarity_scores(text)["compound"]
        if math.isnan(score) or math.isinf(score):
            return 2.0
        return round(score, 4)
    except Exception:
        return 2.0