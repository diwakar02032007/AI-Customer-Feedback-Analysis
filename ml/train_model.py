import os
import sys
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB

# Ensure project root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from ml.preprocessing import preprocess_text
from ml.feature_extraction import get_vectorizer
from utils.logger import logger

def train_and_save_models():
    """Train ML classifiers on multilingual training dataset and save artifacts."""
    datasets_dir = os.path.join(current_dir, 'datasets')
    models_dir = os.path.join(current_dir, 'trained_models')
    os.makedirs(models_dir, exist_ok=True)
    
    training_file = os.path.join(datasets_dir, 'training_data.csv')
    if not os.path.exists(training_file):
        logger.error(f"Training dataset not found at {training_file}")
        return False
        
    df = pd.read_csv(training_file)
    logger.info(f"Loaded {len(df)} training samples.")
    
    # Preprocess text
    df['clean_text'] = df['text'].apply(preprocess_text)
    
    # 1. Vectorizer
    vectorizer = get_vectorizer()
    X = vectorizer.fit_transform(df['clean_text'])
    joblib.dump(vectorizer, os.path.join(models_dir, 'vectorizer.pkl'))
    logger.info("Saved vectorizer.pkl")
    
    # 2. Sentiment Model
    y_sentiment = df['sentiment']
    sentiment_model = LogisticRegression(class_weight='balanced', max_iter=1000)
    sentiment_model.fit(X, y_sentiment)
    joblib.dump(sentiment_model, os.path.join(models_dir, 'sentiment_model.pkl'))
    logger.info("Saved sentiment_model.pkl")
    
    # 3. Category Model
    y_category = df['category']
    category_model = LogisticRegression(class_weight='balanced', max_iter=1000)
    category_model.fit(X, y_category)
    joblib.dump(category_model, os.path.join(models_dir, 'category_model.pkl'))
    logger.info("Saved category_model.pkl")
    
    # 4. Priority Model
    y_priority = df['priority']
    priority_model = LogisticRegression(class_weight='balanced', max_iter=1000)
    priority_model.fit(X, y_priority)
    joblib.dump(priority_model, os.path.join(models_dir, 'priority_model.pkl'))
    logger.info("Saved priority_model.pkl")
    
    logger.info("All ML models trained and saved successfully.")
    return True

if __name__ == '__main__':
    train_and_save_models()
