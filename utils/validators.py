import re
import html

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def is_valid_email(email):
    """Validate email address format."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_password(password):
    """Validate password strength."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""

def sanitize_input(value):
    """Sanitize string against script injection / XSS."""
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    # Strip dangerous HTML tags
    cleaned = html.escape(value.strip())
    return cleaned

def validate_feedback_input(name, email, rating, feedback_text, category="General"):
    """Validate customer feedback submission input."""
    errors = []
    
    if not name or len(name.strip()) < 2:
        errors.append("Customer name must be at least 2 characters.")
    
    if not email or not is_valid_email(email):
        errors.append("Please provide a valid email address.")
        
    try:
        rating_int = int(rating)
        if rating_int < 1 or rating_int > 5:
            errors.append("Rating must be between 1 and 5 stars.")
    except (ValueError, TypeError):
        errors.append("Rating must be an integer between 1 and 5.")
        
    if not feedback_text or len(feedback_text.strip()) < 5:
        errors.append("Feedback text must be at least 5 characters long.")
    elif len(feedback_text.strip()) > 3000:
        errors.append("Feedback text cannot exceed 3,000 characters.")
        
    return len(errors) == 0, errors

def validate_registration_input(name, email, password, confirm_password):
    """Validate user registration inputs."""
    errors = []
    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters.")
    if not email or not is_valid_email(email):
        errors.append("A valid email address is required.")
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters.")
    if password != confirm_password:
        errors.append("Passwords do not match.")
    return len(errors) == 0, errors
