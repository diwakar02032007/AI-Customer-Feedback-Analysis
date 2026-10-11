from datetime import datetime, timezone

def format_datetime(value, fmt="%b %d, %Y %I:%M %p"):
    """Format datetime or string representation into a friendly display format."""
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except Exception:
            try:
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return value
    if isinstance(value, datetime):
        return value.strftime(fmt)
    return str(value)

def format_date(value, fmt="%b %d, %Y"):
    """Format date value."""
    return format_datetime(value, fmt=fmt)

def get_sentiment_badge_class(sentiment):
    """Return Bootstrap badge CSS class for sentiment."""
    s = (sentiment or '').lower()
    if s == 'positive':
        return 'badge-positive'
    elif s == 'negative':
        return 'badge-negative'
    return 'badge-neutral'

def get_priority_badge_class(priority):
    """Return Bootstrap badge CSS class for priority."""
    p = (priority or '').lower()
    if p == 'critical':
        return 'badge-critical'
    elif p == 'high':
        return 'badge-high'
    elif p == 'medium':
        return 'badge-medium'
    return 'badge-low'

def get_status_badge_class(status):
    """Return Bootstrap badge CSS class for status."""
    st = (status or '').lower()
    if st == 'resolved':
        return 'bg-success'
    elif st == 'under_review':
        return 'bg-warning text-dark'
    elif st == 'spam':
        return 'bg-danger'
    return 'bg-primary'

def get_emotion_icon(emotion):
    """Return appropriate emoji and visual icon for detected emotion."""
    e = (emotion or '').lower()
    mapping = {
        'joy': '😊 Joy',
        'anger': '😡 Anger',
        'sadness': '😢 Sadness',
        'fear': '😨 Fear',
        'surprise': '😲 Surprise',
        'neutral': '😐 Neutral'
    }
    return mapping.get(e, f'💬 {e.capitalize()}')

def paginate(items, page=1, per_page=10):
    """Slice an in-memory sequence for pagination."""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = items[start:end]
    total_pages = (total + per_page - 1) // per_page
    return {
        'items': paginated_items,
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': max(1, total_pages),
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1,
        'next_num': page + 1
    }
