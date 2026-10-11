from services.language_service import detect_language
from services.spam_detection_service import detect_spam
from services.sentiment_service import analyze_sentiment
from services.emotion_service import detect_emotion
from services.category_service import classify_category
from services.aspect_service import analyze_aspects
from services.priority_service import determine_priority
from services.summarization_service import summarize_feedback
from services.recommendation_service import generate_recommendation
from services.ollama_service import query_ollama, ollama_analyze_feedback

def run_ai_pipeline(feedback_text, rating=None, user_category=None):
    """
    Execute complete end-to-end AI/NLP feedback analysis pipeline:
    1. Language detection (English, Tamil, Tanglish)
    2. Spam / fake feedback detection
    3. Sentiment analysis and sentiment score
    4. Emotion classification
    5. Category classification
    6. Aspect-based sentiment analysis
    7. Priority detection
    8. Smart summarization
    9. Actionable business recommendation
    """
    # 1. Language Detection
    language = detect_language(feedback_text)

    # 2. Spam & Fake Detection
    spam_prob, is_spam, spam_reason = detect_spam(feedback_text)

    # 3. Sentiment Analysis
    sentiment, sentiment_score = analyze_sentiment(feedback_text, rating=rating)

    # 4. Emotion Detection
    emotion = detect_emotion(feedback_text, sentiment=sentiment)

    # 5. Category Classification
    category = classify_category(feedback_text, user_category=user_category)

    # 6. Aspect-Based Sentiment Analysis (ABSA)
    primary_aspect, aspect_sentiment, aspect_breakdown = analyze_aspects(feedback_text, overall_sentiment=sentiment)

    # 7. Priority Determination
    priority = determine_priority(feedback_text, rating=rating, sentiment=sentiment, emotion=emotion)

    # 8. Summarization & 9. Recommendation (with Ollama enhancement if available)
    ollama_res = None
    if not is_spam:
        ollama_res = ollama_analyze_feedback(feedback_text)

    if ollama_res and isinstance(ollama_res, dict):
        summary = ollama_res.get('summary') or summarize_feedback(feedback_text, sentiment=sentiment, category=category, language=language)
        recommendation = ollama_res.get('recommendation') or generate_recommendation(category=category, sentiment=sentiment, priority=priority, aspect=primary_aspect)
    else:
        summary = summarize_feedback(feedback_text, sentiment=sentiment, category=category, language=language)
        recommendation = generate_recommendation(category=category, sentiment=sentiment, priority=priority, aspect=primary_aspect)

    return {
        'language': language,
        'spam_probability': spam_prob,
        'is_spam': is_spam,
        'spam_reason': spam_reason,
        'sentiment': sentiment,
        'sentiment_score': sentiment_score,
        'emotion': emotion,
        'category': category,
        'aspect': primary_aspect,
        'aspect_sentiment': aspect_sentiment,
        'aspect_breakdown': aspect_breakdown,
        'priority': priority,
        'summary': summary,
        'recommendation': recommendation
    }

__all__ = [
    'run_ai_pipeline',
    'detect_language',
    'detect_spam',
    'analyze_sentiment',
    'detect_emotion',
    'classify_category',
    'analyze_aspects',
    'determine_priority',
    'summarize_feedback',
    'generate_recommendation',
    'query_ollama'
]
