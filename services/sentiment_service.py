import re
from ml.predict import predict_all

# Multilingual Sentiment Lexicons
POSITIVE_TOKENS = {
    # English
    'great', 'excellent', 'outstanding', 'good', 'love', 'best', 'smooth', 'fast',
    'helpful', 'clean', 'intuitive', 'satisfied', 'awesome', 'impressive', 'wonderful',
    'happy', 'super', 'praise', 'courteous', 'quick', 'easy', 'perfect', 'reliable',
    # Tamil Unicode
    'அருமை', 'சிறப்பு', 'நன்று', 'நன்றி', 'மகிழ்ச்சி', 'அற்புதம்', 'உடனடியாக',
    'வேகமாக', 'பயனுள்ள', 'திருப்தி', 'அழகாக', 'நல்வாழ்த்து', 'பாராட்டுகள்',
    # Tanglish
    'nalla', 'nalladhu', 'super-ah', 'supera', 'semma', 'mass', 'marana', 'seekiram',
    'azhaga', 'thirupthi', 'pudichirukku', 'pudichithu', 'alaga', 'clean-ah'
}

NEGATIVE_TOKENS = {
    # English
    'terrible', 'horrible', 'worst', 'bad', 'poor', 'slow', 'crash', 'freeze', 'bug',
    'broken', 'useless', 'waste', 'deducted', 'unresponsive', 'cheat', 'fraud',
    'disappointed', 'fail', 'failed', 'issue', 'problem', 'stuck', 'error', 'scam',
    # Tamil Unicode
    'மோசம்', 'கேவலம்', 'உடைந்து', 'வீண்', 'ஏமாற்று', 'தாமதம்', 'பயனற்றது', 'கோபம்',
    'வேலை செய்யவில்லை', 'பிடித்தம்', 'நம்பகத்தன்மையற்றது', 'முடங்கி',
    # Tanglish
    'mosam', 'mosama', 'keta', 'ketathu', 'waste', 'thappu', 'kashtam', 'kadupu',
    'kadupaguthu', 'slow-va', 'aagala', 'mudiyala', 'pudikkala', 'erithal', 'worst-ah'
}

def analyze_sentiment(text, rating=None):
    """
    Analyze sentiment across English, Tamil, and Tanglish text.
    Combines ML predictions, multilingual lexicon scoring, and customer rating signals.
    Returns:
        sentiment: 'positive', 'neutral', or 'negative'
        sentiment_score: float between -1.00 and 1.00
    """
    if not text:
        return 'neutral', 0.0

    text_lower = text.lower()
    
    # 1. Lexicon scoring
    words = re.findall(r'[\w\u0B80-\u0BFF]+', text_lower)
    pos_count = sum(1 for w in words if w in POSITIVE_TOKENS)
    neg_count = sum(1 for w in words if w in NEGATIVE_TOKENS)

    lexicon_diff = pos_count - neg_count
    
    # 2. ML Prediction
    ml_res = predict_all(text)
    ml_sent = ml_res.get('sentiment', 'neutral')
    ml_score = ml_res.get('sentiment_score', 0.0)

    # 3. Rating Heuristic Bias (-1.0 to 1.0)
    rating_bias = 0.0
    if rating is not None:
        try:
            r = int(rating)
            if r == 5:
                rating_bias = 0.6
            elif r == 4:
                rating_bias = 0.3
            elif r == 3:
                rating_bias = 0.0
            elif r == 2:
                rating_bias = -0.3
            elif r == 1:
                rating_bias = -0.6
        except (ValueError, TypeError):
            pass

    # Blend signals
    combined_score = (ml_score * 0.45) + (min(max(lexicon_diff * 0.25, -0.6), 0.6)) + (rating_bias * 0.30)
    combined_score = round(min(max(combined_score, -1.0), 1.0), 2)

    # Classification threshold
    if combined_score >= 0.18:
        sentiment = 'positive'
    elif combined_score <= -0.18:
        sentiment = 'negative'
    else:
        # If lexicon has explicit polarity, respect it
        if pos_count > neg_count and rating in (4, 5, None):
            sentiment = 'positive'
        elif neg_count > pos_count and rating in (1, 2, None):
            sentiment = 'negative'
        else:
            sentiment = 'neutral'

    # Consistency check with extreme star ratings
    if rating == 5 and sentiment == 'negative' and neg_count == 0:
        sentiment = 'positive'
        combined_score = 0.65
    elif rating == 1 and sentiment == 'positive' and pos_count == 0:
        sentiment = 'negative'
        combined_score = -0.65

    return sentiment, combined_score
