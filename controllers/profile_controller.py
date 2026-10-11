from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.user_model import UserModel
from utils.decorators import login_required
from utils.validators import validate_password
from utils.logger import logger

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route('', methods=['GET', 'POST'])
@profile_bp.route('/', methods=['GET', 'POST'])
@login_required
def view_profile():
    """View and update profile information."""
    user_id = session.get('user_id')
    user = UserModel.get_by_id(user_id)
    if not user:
        flash('User account not found.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_info':
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            bio = request.form.get('bio', '').strip()

            if not name or len(name) < 2:
                flash('Name must be at least 2 characters.', 'danger')
            else:
                UserModel.update_profile(user_id, name, phone, bio)
                session['user_name'] = name
                flash('Profile details updated successfully.', 'success')
                return redirect(url_for('profile.view_profile'))

        elif action == 'change_password':
            current_pass = request.form.get('current_password', '')
            new_pass = request.form.get('new_password', '')
            confirm_pass = request.form.get('confirm_password', '')

            # Verify current password
            auth_user = UserModel.authenticate(user['email'], current_pass)
            if not auth_user:
                flash('Incorrect current password.', 'danger')
            elif new_pass != confirm_pass:
                flash('New passwords do not match.', 'danger')
            else:
                valid, msg = validate_password(new_pass)
                if not valid:
                    flash(msg, 'danger')
                else:
                    UserModel.update_password(user_id, new_pass)
                    flash('Password changed successfully.', 'success')
                    return redirect(url_for('profile.view_profile'))

    return render_template('profile/profile.html', user=user)
