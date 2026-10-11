import os
import joblib
from ml.preprocessing import preprocess_text
from utils.logger import logger

_MODELS = {}

def load_models():
    """Load or lazily initialize ML models from disk."""
    global _MODELS
    if _MODELS:
        return _MODELS

    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trained_models')
    vec_path = os.path.join(models_dir, 'vectorizer.pkl')
    sent_path = os.path.join(models_dir, 'sentiment_model.pkl')
    cat_path = os.path.join(models_dir, 'category_model.pkl')
    prio_path = os.path.join(models_dir, 'priority_model.pkl')

    # If any model is missing, train immediately
    if not (os.path.exists(vec_path) and os.path.exists(sent_path) and os.path.exists(cat_path) and os.path.exists(prio_path)):
        logger.info("ML model pkl files missing. Triggering initial training...")
        from ml.train_model import train_and_save_models
        train_and_save_models()

    try:
        _MODELS['vectorizer'] = joblib.load(vec_path)
        _MODELS['sentiment'] = joblib.load(sent_path)
        _MODELS['category'] = joblib.load(cat_path)
        _MODELS['priority'] = joblib.load(prio_path)
        logger.info("Successfully loaded ML models into memory.")
    except Exception as e:
        logger.error(f"Error loading ML models: {e}")
        
    return _MODELS

def predict_all(text):
    """
    Run Scikit-Learn predictions on input text.
    Returns dict: sentiment, sentiment_score, category, priority.
    """
    clean = preprocess_text(text)
    if not clean:
        return {
            'sentiment': 'neutral',
            'sentiment_score': 0.0,
            'category': 'General',
            'priority': 'low'
        }

    models = load_models()
    if not models or 'vectorizer' not in models:
        return {
            'sentiment': 'neutral',
            'sentiment_score': 0.0,
            'category': 'General',
            'priority': 'low'
        }

    vec = models['vectorizer']
    X = vec.transform([clean])

    # 1. Sentiment prediction
    sentiment_model = models.get('sentiment')
    sentiment = 'neutral'
    sentiment_score = 0.0
    if sentiment_model:
        pred_sent = sentiment_model.predict(X)[0]
        sentiment = str(pred_sent)
        if hasattr(sentiment_model, 'predict_proba'):
            classes = list(sentiment_model.classes_)
            probs = sentiment_model.predict_proba(X)[0]
            prob_dict = dict(zip(classes, probs))
            pos_prob = prob_dict.get('positive', 0.33)
            neg_prob = prob_dict.get('negative', 0.33)
            sentiment_score = round(float(pos_prob - neg_prob), 2)

    # 2. Category prediction
    cat_model = models.get('category')
    category = 'General'
    if cat_model:
        category = str(cat_model.predict(X)[0])

    # 3. Priority prediction
    prio_model = models.get('priority')
    priority = 'low'
    if prio_model:
        priority = str(prio_model.predict(X)[0])

    return {
        'sentiment': sentiment,
        'sentiment_score': sentiment_score,
        'category': category,
        'priority': priority
    }
