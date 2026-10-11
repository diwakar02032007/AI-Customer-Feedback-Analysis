import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app

class TestDashboard(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

    def login_as_admin(self):
        """Helper to simulate logged-in admin session."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin User'
            sess['user_email'] = 'admin@feedbackai.com'
            sess['user_role'] = 'admin'

    def test_admin_dashboard_protected(self):
        """Unauthenticated requests must be redirected to login."""
        res = self.client.get('/admin/dashboard', follow_redirects=False)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/auth/login', res.headers['Location'])

    def test_admin_dashboard_access_authorized(self):
        """Authorized admin should get 200 OK."""
        self.login_as_admin()
        res = self.client.get('/admin/dashboard')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Customer Intelligence Overview', res.data)
        self.assertIn(b'Executive AI Dashboard', res.data)

    def test_analytics_api_endpoint(self):
        """Test analytics JSON API returns structured telemetry data."""
        self.login_as_admin()
        res = self.client.get('/api/analytics-data')
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertIn('kpis', json_data)
        self.assertIn('trends', json_data)
        self.assertIn('categories', json_data)
        self.assertIn('emotions', json_data)

    def test_csv_export_endpoint(self):
        """Test feedback CSV download endpoint."""
        self.login_as_admin()
        res = self.client.get('/admin/reports/export-csv')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, 'text/csv; charset=utf-8')
        self.assertIn(b'Feedback ID,Customer Name,Customer Email', res.data)

if __name__ == '__main__':
    unittest.main()
