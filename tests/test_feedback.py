import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from models.feedback_model import FeedbackModel
from services import run_ai_pipeline

class TestFeedback(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_pipeline_execution(self):
        """Test full AI pipeline execution return values."""
        res = run_ai_pipeline("The customer support was lightning fast and courteous.", rating=5, user_category="Customer Support")
        self.assertEqual(res['sentiment'], 'positive')
        self.assertEqual(res['category'], 'Customer Support')
        self.assertFalse(res['is_spam'])
        self.assertIsNotNone(res['summary'])
        self.assertIsNotNone(res['recommendation'])

    def test_feedback_submission_and_retrieval(self):
        """Test inserting and retrieving feedback in database."""
        pipeline_data = run_ai_pipeline("Super fast delivery within 12 hours!", rating=5)
        data = {
            'user_id': 2,
            'customer_name': 'Test Customer',
            'customer_email': 'test@example.com',
            'rating': 5,
            'feedback_text': 'Super fast delivery within 12 hours!',
            'category': pipeline_data['category'],
            'status': 'new',
            'priority': pipeline_data['priority'],
            'sentiment': pipeline_data['sentiment'],
            'sentiment_score': pipeline_data['sentiment_score'],
            'emotion': pipeline_data['emotion'],
            'aspect': pipeline_data['aspect'],
            'aspect_sentiment': pipeline_data['aspect_sentiment'],
            'spam_probability': pipeline_data['spam_probability'],
            'is_spam': pipeline_data['is_spam'],
            'language': pipeline_data['language'],
            'summary': pipeline_data['summary'],
            'recommendation': pipeline_data['recommendation']
        }
        f_id = FeedbackModel.create(data, aspect_breakdown=pipeline_data['aspect_breakdown'])
        self.assertIsNotNone(f_id)

        # Retrieve
        fetched = FeedbackModel.get_by_id(f_id)
        self.assertEqual(fetched['customer_name'], 'Test Customer')
        self.assertEqual(fetched['sentiment'], 'positive')

        # Status Update
        FeedbackModel.update_status(f_id, status='resolved', admin_notes='Issue addressed')
        updated = FeedbackModel.get_by_id(f_id)
        self.assertEqual(updated['status'], 'resolved')
        self.assertEqual(updated['admin_notes'], 'Issue addressed')

    def test_live_preview_api(self):
        """Test live analysis API JSON endpoint."""
        response = self.client.post('/api/analyze-live', json={
            'text': 'The user interface is amazingly smooth and clean.',
            'rating': 5,
            'category': 'Usability/UI'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['sentiment'], 'positive')
        self.assertEqual(data['emotion'], 'joy')

if __name__ == '__main__':
    unittest.main()
