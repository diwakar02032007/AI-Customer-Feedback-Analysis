import re
from ml.predict import predict_all

CATEGORY_KEYWORDS = {
    'Product Quality': {
        'quality', 'build', 'material', 'durability', 'hardware', 'broken', 'defective', 'damage',
        'தரம்', 'உடைந்து', 'பொருள்', 'பழுது', 'build quality', 'item'
    },
    'Customer Support': {
        'support', 'agent', 'executive', 'representative', 'ticket', 'helpdesk', 'call', 'chat',
        'சேவை', 'உதவி', 'பதில்', 'customer care', 'care number', 'help'
    },
    'Billing/Pricing': {
        'billing', 'price', 'pricing', 'charge', 'charged', 'deducted', 'refund', 'invoice',
        'subscription', 'payment', 'money', 'expensive', 'cost', 'கட்டணம்', 'பணம்', 'விலை',
        'checkout', 'auto-debit', 'kaasu'
    },
    'Delivery/Speed': {
        'delivery', 'shipping', 'courier', 'speed', 'delay', 'tracking', 'package', 'arrived',
        'transit', 'விநியோகம்', 'டெலிவரி', 'தாமதம்', 'seekiram', 'late delivery'
    },
    'Usability/UI': {
        'ui', 'ux', 'interface', 'design', 'layout', 'navigation', 'button', 'screen', 'theme',
        'app', 'crash', 'login', 'bug', 'slow', 'dark mode', 'பயன்பாடு', 'திரை'
    }
}

def classify_category(text, user_category=None):
    """
    Classify customer feedback into product/service category.
    Returns standard category string.
    """
    if user_category and user_category != 'General':
        return user_category

    if not text:
        return 'General'

    text_lower = text.lower()
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}

    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[cat] += 1

    top_cat = max(scores, key=scores.get)
    if scores[top_cat] > 0:
        return top_cat

    # Fallback to ML classification
    ml_res = predict_all(text)
    return ml_res.get('category', 'General')
