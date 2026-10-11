from sklearn.feature_extraction.text import TfidfVectorizer

def get_vectorizer():
    """Build and configure a TF-IDF vectorizer suited for multilingual and Tanglish text."""
    return TfidfVectorizer(
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=1,
        max_features=4000,
        token_pattern=r'(?u)\b\w+\b'
    )
