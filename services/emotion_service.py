import re

EMOTION_KEYWORDS = {
    'anger': {
        'terrible', 'horrible', 'worst', 'cheat', 'fraud', 'scam', 'refund', 'money deducted',
        'stolen', 'ridiculous', 'hate', 'furious', 'anger', 'unacceptable',
        'கோபம்', 'ஏமாற்று', 'மோசம்', 'கேவலம்', 'திருட்டு', 'அயோக்கியத்தனம்',
        'kadupaguthu', 'kadupu', 'erithal', 'waste-ah', 'thirumbi kudu'
    },
    'joy': {
        'love', 'great', 'awesome', 'excellent', 'fantastic', 'happy', 'smooth', 'best',
        'thank you', 'thanks', 'kudos', 'delight', 'wonderful', 'pleased',
        'அருமை', 'மகிழ்ச்சி', 'நன்றி', 'அற்புதம்', 'சிறப்பு',
        'super-ah', 'semma', 'mass', 'pudichirukku', 'happy-ah'
    },
    'sadness': {
        'sad', 'disappointed', 'unfortunate', 'regret', 'poor', 'slow', 'depressed',
        'unhappy', 'missed', 'pity', 'hopeless', 'waiting for days',
        'வருத்தம்', 'கவலை', 'ஏமாற்றம்', 'தாமதம்',
        'kashtam', 'mudiyala', 'romba delay', 'manasu kashtama irukku'
    },
    'fear': {
        'fear', 'scared', 'worried', 'hacked', 'data leak', 'stolen credentials',
        'compromised', 'unsafe', 'risk', 'dangerous', 'lost access',
        'பயம்', 'அச்சம்', 'ஆபத்து', 'பாதுகாப்பற்ற',
        'bayama irukku', 'bayam', 'risk-ah'
    },
    'surprise': {
        'wow', 'surprised', 'unexpected', 'amazed', 'shocked', 'astonishing',
        'ஆச்சரியம்', 'வியப்பு', 'நம்ப முடியவில்லை', 'adhirchi', 'shock aaiten'
    }
}

def detect_emotion(text, sentiment='neutral'):
    """
    Detect primary human emotion from customer feedback text.
    Returns: 'joy', 'anger', 'sadness', 'fear', 'surprise', or 'neutral'
    """
    if not text:
        return 'neutral'

    text_lower = text.lower()
    scores = {emotion: 0 for emotion in EMOTION_KEYWORDS}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[emotion] += 1

    # Find highest matching emotion
    top_emotion = max(scores, key=scores.get)
    if scores[top_emotion] > 0:
        return top_emotion

    # Fallback based on sentiment
    if sentiment == 'positive':
        return 'joy'
    elif sentiment == 'negative':
        return 'sadness'
    return 'neutral'
