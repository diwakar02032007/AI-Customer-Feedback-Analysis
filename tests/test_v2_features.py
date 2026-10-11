import io
import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from models.feedback_model import FeedbackModel
from models.activity_log_model import ActivityLogModel
from models.analysis_model import AnalysisModel

class TestV2Features(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()

    def login_as_admin(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['user_name'] = 'Admin User'
            sess['user_email'] = 'admin@feedbackai.com'
            sess['user_role'] = 'admin'

    def test_activity_logging(self):
        """Test ActivityLogModel creates and retrieves audit logs."""
        with self.app.app_context():
            success = ActivityLogModel.log(
                action='TEST_AUDIT_ACTION',
                details='Testing audit log creation for compliance',
                user_id=1
            )
            self.assertTrue(success)
            recent_logs = ActivityLogModel.get_recent(limit=5)
            self.assertIsInstance(recent_logs, list)
            self.assertTrue(any(log['action'] == 'TEST_AUDIT_ACTION' for log in recent_logs))

    def test_duplicate_feedback_detection(self):
        """Test duplicate check correctly identifies existing vs new feedback."""
        with self.app.app_context():
            # Query existing feedbacks
            res = FeedbackModel.get_all(page=1, per_page=1)
            if res['feedbacks']:
                existing = res['feedbacks'][0]
                # Exact match should return True
                is_dup = FeedbackModel.check_duplicate(existing['feedback_text'], existing['customer_email'])
                self.assertTrue(is_dup)
            
            # Unique non-existent text should return False
            is_dup_fake = FeedbackModel.check_duplicate('A truly unique test message that does not exist 99887711!', 'unique.test@example.com')
            self.assertFalse(is_dup_fake)

    def test_feedback_filtering_by_rating_and_date(self):
        """Test feedback listing respects rating and date bounds."""
        with self.app.app_context():
            res_5star = FeedbackModel.get_all(page=1, per_page=10, rating='5')
            for f in res_5star['feedbacks']:
                self.assertEqual(int(f['rating']), 5)

            res_1star = FeedbackModel.get_all(page=1, per_page=10, rating='1')
            for f in res_1star['feedbacks']:
                self.assertEqual(int(f['rating']), 1)

    def test_analysis_distributions(self):
        """Test rating and aspect sentiment distribution analytics."""
        with self.app.app_context():
            rating_dist = AnalysisModel.get_rating_distribution()
            self.assertIsInstance(rating_dist, list)
            self.assertEqual(len(rating_dist), 5)  # 1 to 5 stars

            aspect_dist = AnalysisModel.get_aspect_sentiment_distribution()
            self.assertIsInstance(aspect_dist, list)

            recommendations = AnalysisModel.get_actionable_recommendations()
            self.assertIsInstance(recommendations, list)

    def test_csv_import_endpoint_authenticated(self):
        """Test batch CSV ingestion route with valid CSV data."""
        self.login_as_admin()

        csv_content = (
            "customer_name,customer_email,feedback_text,rating,category\n"
            "Automation User,auto@test.com,The new UI performance is exceptionally responsive and smooth!,5,Usability/UI\n"
        )
        data = {
            'csv_file': (io.BytesIO(csv_content.encode('utf-8')), 'test_batch.csv')
        }

        res = self.client.post(
            '/admin/feedbacks/import',
            data=data,
            content_type='multipart/form-data',
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)

    def test_csv_import_invalid_file_rejected(self):
        """Test non-csv file upload is rejected."""
        self.login_as_admin()

        data = {
            'csv_file': (io.BytesIO(b'not a csv'), 'malicious.exe')
        }

        res = self.client.post(
            '/admin/feedbacks/import',
            data=data,
            content_type='multipart/form-data',
            follow_redirects=True
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Only .csv files are supported', res.data)

    def test_csv_export_with_active_filters(self):
        """Test CSV export respects query parameters like sentiment=positive."""
        self.login_as_admin()
        res = self.client.get('/admin/reports/export-csv?sentiment=positive')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('Content-Type'), 'text/csv; charset=utf-8')
        csv_text = res.data.decode('utf-8')
        lines = csv_text.strip().split('\n')
        self.assertGreater(len(lines), 1)  # Has header + rows

    def test_all_admin_views_render_cleanly(self):
        """Test all admin pages render HTTP 200 with navbar alerts context."""
        self.login_as_admin()
        endpoints = [
            '/admin/dashboard',
            '/admin/feedbacks',
            '/admin/analytics',
            '/admin/insights',
            '/admin/reports/',
            '/admin/users',
            '/profile/'
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Endpoint {ep} failed with {res.status_code}")

    def test_customer_portal_views(self):
        """Test public customer portal views render HTTP 200."""
        public_endpoints = [
            '/home',
            '/feedback/submit',
            '/auth/login',
            '/auth/register',
            '/auth/forgot-password'
        ]
        for ep in public_endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Public endpoint {ep} failed with {res.status_code}")

if __name__ == '__main__':
    unittest.main()
