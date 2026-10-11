from functools import wraps
from flask import session, redirect, url_for, flash, request, abort

def login_required(f):
    """Ensure user is logged in before accessing route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Ensure current user is authenticated with admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in as an administrator.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        if session.get('user_role') != 'admin':
            flash('Access denied: Administrator privileges required.', 'danger')
            return redirect(url_for('customer.home'))
        return f(*args, **kwargs)
    return decorated_function

def customer_required(f):
    """Ensure user has a customer or admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function
