import re

CRITICAL_TRIGGERS = {
    'deducted twice', 'money deducted', 'refund immediately', 'fraud', 'cheat', 'scam',
    'legal action', 'sue', 'police', 'stolen', 'double charged', 'unresponsive for days',
    'lost data', 'server down', 'breach', 'emergency', 'பணத்தை திருப்பி', 'ஏமாற்று'
}

HIGH_TRIGGERS = {
    'broken', 'not working', 'horrible', 'terrible', 'worst', 'urgent', 'disaster',
    'login failed', 'crash', 'cannot access', 'blocked', 'mosam', 'உடைந்து'
}

def determine_priority(text, rating=3, sentiment='neutral', emotion='neutral'):
    """
    Determine automated response priority: 'critical', 'high', 'medium', or 'low'.
    Combines text urgency signals, rating, sentiment polarity, and emotional intensity.
    """
    if not text:
        return 'low'

    text_lower = text.lower()
    try:
        rating_val = int(rating)
    except (ValueError, TypeError):
        rating_val = 3

    # 1. Critical condition
    for trigger in CRITICAL_TRIGGERS:
        if trigger in text_lower:
            return 'critical'

    if rating_val == 1 and (sentiment == 'negative' or emotion == 'anger'):
        for trigger in HIGH_TRIGGERS:
            if trigger in text_lower:
                return 'critical'
        return 'high'

    # 2. High priority
    if rating_val <= 2 and sentiment == 'negative':
        return 'high'
    if emotion == 'anger' and rating_val <= 3:
        return 'high'

    # 3. Medium priority
    if rating_val == 3:
        return 'medium'
    if rating_val in (1, 2) and sentiment != 'negative':
        return 'medium'
    if rating_val >= 4 and sentiment == 'negative':
        return 'medium'

    # 4. Low priority
    return 'low'
