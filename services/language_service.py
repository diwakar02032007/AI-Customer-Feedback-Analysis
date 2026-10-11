import re
from utils.text_utils import contains_tamil, contains_tanglish

def detect_language(text):
    """
    Detect the primary language of the customer feedback:
    - Tamil (Native Tamil script)
    - Tanglish (Phonetic Tamil transliterated in Latin alphabet)
    - English (Standard English)
    """
    if not text:
        return "English"
    
    # 1. Native Tamil script check
    if contains_tamil(text):
        return "Tamil"
        
    # 2. Tanglish check (phonetic markers)
    if contains_tanglish(text):
        return "Tanglish"
        
    # 3. Default to English
    return "English"
