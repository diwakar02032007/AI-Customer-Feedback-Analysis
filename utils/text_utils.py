import re
import html

# Common Tanglish lexicon markers
TANGLISH_PATTERNS = {
    'romba', 'romba-ah', 'nalla', 'nalladhu', 'nallaa', 'super-ah', 'supera',
    'irukku', 'iruku', 'irukkum', 'aaguthu', 'aagala', 'aavathu', 'mosam',
    'mosama', 'keta', 'ketathu', 'illai', 'ila', 'illa', 'pannunga', 'panreenga',
    'kadupaguthu', 'kashtam', 'solren', 'porumai', 'thappu', 'kodunga', 'venum',
    'vendam', 'konjam', 'mattum', 'seri', 'seriya', 'theriyala', 'pudikkala',
    'valithu', 'udane', 'seekiram', 'kedaikala', 'panren', 'nanri', 'vanakkam',
    'solla', 'mudiyala', 'mudiyathu', 'thirumbi', 'panam', 'kaasu'
}

def clean_text(text):
    """Clean and sanitize text string."""
    if not text:
        return ""
    # Unescape HTML entities
    text = html.unescape(str(text))
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Normalize multiple whitespace characters
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def contains_tamil(text):
    """Detect if text contains Tamil Unicode script (U+0B80 to U+0BFF)."""
    if not text:
        return False
    tamil_range = re.compile(r'[\u0B80-\u0BFF]')
    return bool(tamil_range.search(text))

def contains_tanglish(text):
    """Detect if Latin-script text contains phonetic Tamil / Tanglish words."""
    if not text or contains_tamil(text):
        return False
    words = re.findall(r'[a-zA-Z]+', text.lower())
    if not words:
        return False
    tanglish_count = sum(1 for w in words if w in TANGLISH_PATTERNS)
    ratio = tanglish_count / len(words)
    return tanglish_count >= 1 and (ratio >= 0.10 or tanglish_count >= 2)

def extract_keywords(text, top_n=5):
    """Extract frequent informative words."""
    if not text:
        return []
    words = re.findall(r'\b[a-zA-Z\u0B80-\u0BFF]{4,}\b', text.lower())
    stopwords = {
        'this', 'that', 'with', 'from', 'have', 'were', 'they', 'what', 'when',
        'your', 'about', 'some', 'will', 'there', 'their', 'very', 'been',
        'just', 'more', 'also', 'than', 'them', 'then', 'these', 'could',
        'would', 'other', 'into', 'only', 'which', 'after'
    }
    freq = {}
    for w in words:
        if w not in stopwords:
            freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [w[0] for w in sorted_words[:top_n]]

def truncate_text(text, max_len=100):
    """Truncate long text with ellipsis."""
    if not text:
        return ""
    text = clean_text(text)
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(' ', 1)[0] + '...'
