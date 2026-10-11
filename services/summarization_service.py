import re
from utils.text_utils import truncate_text, clean_text, contains_tamil, contains_tanglish

def summarize_feedback(text, sentiment='neutral', category='General', language='English'):
    """
    Generate a concise, crisp executive summary of customer feedback.
    Supports English, Tamil, and Tanglish feedback.
    """
    if not text:
        return "No feedback content provided."

    clean = clean_text(text)
    
    # Language-aware smart summaries
    if language == 'Tamil':
        if sentiment == 'positive':
            return f"வாடிக்கையாளர் {category} சேவையில் மிகுந்த திருப்தி மற்றும் பாராட்டு தெரிவித்துள்ளார்."
        elif sentiment == 'negative':
            return f"வாடிக்கையாளர் {category} தொடர்பாக அதிருப்தி தெரிவித்து உடனடி தீர்வு கோரியுள்ளார்."
        return f"{category} தொடர்பான வாடிக்கையாளரின் கருத்து பதிவு செய்யப்பட்டுள்ளது."

    if language == 'Tanglish':
        if sentiment == 'positive':
            return f"Customer expressed positive satisfaction regarding {category} in Tanglish."
        elif sentiment == 'negative':
            return f"Customer reported critical issues/dissatisfaction regarding {category} in Tanglish."
        return f"Customer shared neutral feedback regarding {category}."

    # For English: extract core sentence or formulate summary
    sentences = re.split(r'[.!?]+', clean)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]

    if not sentences:
        return truncate_text(clean, 120)

    # First informative sentence
    core = sentences[0]
    if len(core) < 140:
        return core + "."
    return truncate_text(core, 130)
