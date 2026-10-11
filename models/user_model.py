from werkzeug.security import generate_password_hash, check_password_hash
from database.db import execute_query
from utils.logger import logger

class UserModel:
    @staticmethod
    def get_by_id(user_id):
        """Fetch user by primary key ID."""
        query = "SELECT id, name, email, role, phone, avatar, bio, created_at FROM users WHERE id = %s"
        return execute_query(query, (user_id,), fetch='one')

    @staticmethod
    def get_by_email(email):
        """Fetch user by unique email."""
        query = "SELECT * FROM users WHERE email = %s"
        return execute_query(query, (email.strip().lower(),), fetch='one')

    @staticmethod
    def create(name, email, password, role='customer', phone=None, bio=None):
        """Create new user account."""
        password_hash = generate_password_hash(password)
        query = """
            INSERT INTO users (name, email, password_hash, role, phone, bio)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        user_id = execute_query(query, (name.strip(), email.strip().lower(), password_hash, role, phone, bio), commit=True)
        return user_id

    @staticmethod
    def authenticate(email, password):
        """Verify user credentials and return user object if valid."""
        user = UserModel.get_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None

    @staticmethod
    def update_profile(user_id, name, phone=None, bio=None, avatar=None):
        """Update user profile information."""
        if avatar:
            query = "UPDATE users SET name = %s, phone = %s, bio = %s, avatar = %s WHERE id = %s"
            params = (name.strip(), phone, bio, avatar, user_id)
        else:
            query = "UPDATE users SET name = %s, phone = %s, bio = %s WHERE id = %s"
            params = (name.strip(), phone, bio, user_id)
        return execute_query(query, params, commit=True)

    @staticmethod
    def update_password(user_id, new_password):
        """Update user password with secure hash."""
        password_hash = generate_password_hash(new_password)
        query = "UPDATE users SET password_hash = %s WHERE id = %s"
        return execute_query(query, (password_hash, user_id), commit=True)

    @staticmethod
    def get_all(page=1, per_page=10):
        """Fetch paginated users."""
        count_query = "SELECT COUNT(*) as cnt FROM users"
        total_res = execute_query(count_query, fetch='one')
        total = total_res['cnt'] if total_res else 0

        offset = (page - 1) * per_page
        query = "SELECT id, name, email, role, phone, avatar, created_at FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s"
        users = execute_query(query, (per_page, offset), fetch='all') or []
        
        total_pages = max(1, (total + per_page - 1) // per_page)
        return {
            'users': users,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'prev_num': page - 1,
            'has_next': page < total_pages,
            'next_num': page + 1
        }

