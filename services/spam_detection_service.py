import re

SPAM_KEYWORDS = {
    'click here', 'buy cheap', 'discount 90%', 'free gift', 'winner',
    'cash prize', 'bitcoin', 'crypto', 'earn money', 'work from home',
    'make millions', 'casino', 'viagra', 'telegram bot', 'whatsapp group link',
    'http://spam', 'investment guaranteed', 'lottery', 'claim bonus'
}

def detect_spam(text):
    """
    Evaluate feedback text for spam and fake submission patterns.
    Returns:
        spam_probability (float: 0.0 to 1.0)
        is_spam (bool)
        spam_reason (str)
    """
    if not text:
        return 0.0, False, "Clean"

    text_lower = text.lower()
    score = 0.0
    reasons = []

    # 1. URL pattern check
    url_matches = re.findall(r'https?://\S+|www\.\S+', text)
    if url_matches:
        score += 0.45
        reasons.append("Contains suspicious link")

    # 2. Known spam keywords
    matched_spam_keywords = [kw for kw in SPAM_KEYWORDS if kw in text_lower]
    if matched_spam_keywords:
        score += 0.40 * len(matched_spam_keywords)
        reasons.append(f"Spam phrases detected ({', '.join(matched_spam_keywords[:2])})")

    # 3. Excessive capital letters
    letters = [c for c in text if c.isalpha()]
    if letters:
        caps = [c for c in letters if c.isupper()]
        caps_ratio = len(caps) / len(letters)
        if len(letters) > 15 and caps_ratio > 0.65:
            score += 0.25
            reasons.append("Excessive uppercase text")

    # 4. Repeated character sequence (e.g., 'aaaaaa', '!!!!!!', '$$$$$')
    if re.search(r'(.)\1{5,}', text) or re.search(r'[\$!]{3,}', text):
        score += 0.20
        reasons.append("Excessive symbol/character repetition")

    # 5. Keyboard smash check
    if re.search(r'\b(?:asdfgh|qwertyui|zxcvbn)\b', text_lower):
        score += 0.40
        reasons.append("Random keystroke pattern")

    spam_probability = min(1.0, round(score, 2))
    is_spam = spam_probability >= 0.60
    reason_str = "; ".join(reasons) if reasons else "Legitimate customer feedback"

    return spam_probability, is_spam, reason_str
