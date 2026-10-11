import re
import html
from utils.text_utils import clean_text

def preprocess_text(text):
    """
    Preprocess raw text for NLP feature extraction.
    Supports English, Tamil Unicode, and Tanglish transliterations.
    """
    if not text:
        return ""
    
    # Basic cleaning
    text = clean_text(text)
    
    # Replace URLs and emails with special tokens
    text = re.sub(r'https?://\S+|www\.\S+', ' url_token ', text)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', ' email_token ', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Preserve English alphabets, digits, and Tamil Unicode range (\u0B80-\u0BFF)
    # Replace other punctuation with spaces
    text = re.sub(r'[^\w\s\u0B80-\u0BFF]', ' ', text)
    
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text
