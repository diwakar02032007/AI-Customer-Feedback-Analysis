import re

ASPECT_PATTERNS = {
    'UI/UX': ['ui', 'ux', 'interface', 'design', 'layout', 'navigation', 'theme', 'look', 'visual', 'திரை'],
    'Customer Support': ['support', 'agent', 'executive', 'help', 'ticket', 'call', 'chat', 'சேவை', 'உதவி'],
    'Pricing': ['price', 'pricing', 'charge', 'cost', 'expensive', 'refund', 'subscription', 'billing', 'விலை', 'பணம்'],
    'Features/Performance': ['feature', 'crash', 'speed', 'slow', 'performance', 'battery', 'lag', 'loading', 'bug'],
    'Delivery/Speed': ['delivery', 'courier', 'shipping', 'package', 'transit', 'tracking', 'விநியோகம்', 'டெலிவரி'],
    'Product Quality': ['quality', 'build', 'durability', 'material', 'hardware', 'தரம்', 'உடைந்து']
}

def analyze_aspects(text, overall_sentiment='neutral'):
    """
    Perform Aspect-Based Sentiment Analysis (ABSA).
    Returns:
        primary_aspect (str)
        aspect_sentiment (str)
        aspect_breakdown (list of dicts)
    """
    if not text:
        return 'General', overall_sentiment, [{'aspect_name': 'General', 'sentiment': overall_sentiment, 'confidence': 1.0}]

    text_lower = text.lower()
    detected_aspects = []

    for aspect, keywords in ASPECT_PATTERNS.items():
        matched = [kw for kw in keywords if re.search(rf'\b{re.escape(kw)}\b', text_lower)]
        if matched:
            detected_aspects.append({
                'aspect_name': aspect,
                'sentiment': overall_sentiment,
                'confidence': 0.85 + min(0.10, len(matched) * 0.05)
            })

    if not detected_aspects:
        detected_aspects.append({
            'aspect_name': 'General',
            'sentiment': overall_sentiment,
            'confidence': 0.75
        })

    primary_aspect = detected_aspects[0]['aspect_name']
    aspect_sentiment = detected_aspects[0]['sentiment']

    return primary_aspect, aspect_sentiment, detected_aspects
