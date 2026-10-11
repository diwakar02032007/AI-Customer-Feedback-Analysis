import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app import create_app
from models.analysis_model import AnalysisModel

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_dashboard_kpis(self):
        """Test calculation of dashboard KPIs and satisfaction metrics."""
        kpis = AnalysisModel.get_dashboard_kpis()
        self.assertIn('total_feedback', kpis)
        self.assertIn('avg_rating', kpis)
        self.assertIn('csat_score', kpis)
        self.assertIn('nps_score', kpis)
        self.assertGreater(kpis['total_feedback'], 0)

    def test_category_distribution(self):
        """Test category distribution query."""
        cats = AnalysisModel.get_category_distribution()
        self.assertIsInstance(cats, list)
        self.assertGreater(len(cats), 0)

    def test_emotion_distribution(self):
        """Test emotion distribution aggregation."""
        emotions = AnalysisModel.get_emotion_distribution()
        self.assertIsInstance(emotions, list)
        self.assertGreater(len(emotions), 0)

    def test_sentiment_trends(self):
        """Test sentiment timeline query."""
        trends = AnalysisModel.get_sentiment_trends(days=14)
        self.assertIsInstance(trends, list)

if __name__ == '__main__':
    unittest.main()
