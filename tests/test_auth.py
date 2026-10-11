import os
import sys
import unittest

# Ensure project path is accessible
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from database.db import get_db, init_db
from models.user_model import UserModel

class TestAuth(unittest.TestCase):
    def setUp(self):
        # Configure app in testing mode
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_user_authentication_success(self):
        """Test valid authentication against seeded admin user."""
        user = UserModel.authenticate('admin@feedbackai.com', 'AdminPassword123!')
        self.assertIsNotNone(user)
        self.assertEqual(user['role'], 'admin')

    def test_user_authentication_failure(self):
        """Test authentication fails on wrong password."""
        user = UserModel.authenticate('admin@feedbackai.com', 'WrongPassword!')
        self.assertIsNone(user)

    def test_registration_flow(self):
        """Test registering a new unique user."""
        email = f"testuser_{os.urandom(3).hex()}@example.com"
        user_id = UserModel.create(name="Test User", email=email, password="ValidPassword123!", role="customer")
        self.assertIsNotNone(user_id)
        
        # Test authenticating new user
        auth_user = UserModel.authenticate(email, "ValidPassword123!")
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user['name'], "Test User")

    def test_login_route_success(self):
        """Test login endpoint redirecting to admin dashboard."""
        response = self.client.post('/auth/login', data={
            'email': 'admin@feedbackai.com',
            'password': 'AdminPassword123!'
        }, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/dashboard', response.headers['Location'])

if __name__ == '__main__':
    unittest.main()
