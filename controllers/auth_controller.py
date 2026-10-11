from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user_model import UserModel
from utils.validators import validate_registration_input, is_valid_email
from utils.logger import logger

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login for both Admin and Customer roles."""
    if 'user_id' in session:
        if session.get('user_role') == 'admin':
            return redirect(url_for('dashboard.admin_dashboard'))
        return redirect(url_for('customer.home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash('Please enter both email and password.', 'warning')
            return render_template('auth/login.html', email=email)

        user = UserModel.authenticate(email, password)
        if user:
            # Set session
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']
            session.permanent = remember

            flash(f"Welcome back, {user['name']}!", 'success')
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)

            if user['role'] == 'admin':
                return redirect(url_for('dashboard.admin_dashboard'))
            return redirect(url_for('customer.home'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new customer registration."""
    if 'user_id' in session:
        return redirect(url_for('customer.home'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()

        is_valid, errors = validate_registration_input(name, email, password, confirm_password)
        if not is_valid:
            for err in errors:
                flash(err, 'danger')
            return render_template('auth/register.html', name=name, email=email, phone=phone)

        # Check existing email
        existing_user = UserModel.get_by_email(email)
        if existing_user:
            flash('An account with this email already exists. Please log in.', 'warning')
            return redirect(url_for('auth.login'))

        # Create account
        user_id = UserModel.create(name=name, email=email, password=password, role='customer', phone=phone)
        if user_id:
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Registration failed due to a server issue. Please try again.', 'danger')

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    """Log out current user and clear session."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password request."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'danger')
        else:
            user = UserModel.get_by_email(email)
            if user:
                flash('Password reset instructions have been sent to your email address.', 'info')
            else:
                flash('If an account exists for that email, password instructions have been sent.', 'info')
            return redirect(url_for('auth.login'))
            
    return render_template('auth/forgot_password.html')
