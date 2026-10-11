import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.sentiment_service import analyze_sentiment
from services.emotion_service import detect_emotion
from services.language_service import detect_language
from services.spam_detection_service import detect_spam
from services.priority_service import determine_priority

class TestSentimentAndNLP(unittest.TestCase):
    def test_english_sentiment(self):
        """Test English positive and negative sentiment analysis."""
        pos_text = "The user interface is amazingly fast and intuitive. Best software update!"
        sentiment, score = analyze_sentiment(pos_text, rating=5)
        self.assertEqual(sentiment, 'positive')
        self.assertGreater(score, 0)

        neg_text = "Checkout page crashes every time I click pay. Money got debited but order failed!"
        sentiment, score = analyze_sentiment(neg_text, rating=1)
        self.assertEqual(sentiment, 'negative')
        self.assertLess(score, 0)

    def test_tamil_language_and_sentiment(self):
        """Test Native Tamil text detection and sentiment."""
        tamil_text = "வாடிக்கையாளர் சேவை மிகவும் அருமை. உடனடியாக பதில் கிடைத்தது. நன்றி!"
        lang = detect_language(tamil_text)
        self.assertEqual(lang, 'Tamil')
        sentiment, score = analyze_sentiment(tamil_text, rating=5)
        self.assertEqual(sentiment, 'positive')

    def test_tanglish_detection_and_sentiment(self):
        """Test Tanglish phonetic text detection and sentiment."""
        tanglish_text = "App romba slow-va irukku. Login panna 2 minutes aaguthu. Fix pannunga."
        lang = detect_language(tanglish_text)
        self.assertEqual(lang, 'Tanglish')
        sentiment, _ = analyze_sentiment(tanglish_text, rating=1)
        self.assertEqual(sentiment, 'negative')

    def test_emotion_detection(self):
        """Test emotion detection for joy and anger."""
        joy_text = "Thank you so much! I love this product, it is wonderful!"
        self.assertEqual(detect_emotion(joy_text, sentiment='positive'), 'joy')

        anger_text = "Horrible cheat and fraud! Deducted money twice and support is useless!"
        self.assertEqual(detect_emotion(anger_text, sentiment='negative'), 'anger')

    def test_spam_detection(self):
        """Test spam detection on promotional spam vs clean feedback."""
        spam_text = "CLICK HERE FOR FREE BITCOIN 1000 DOLLARS BONUS WINNER http://spamlink.xyz"
        prob, is_spam, _ = detect_spam(spam_text)
        self.assertTrue(is_spam)
        self.assertGreaterEqual(prob, 0.60)

        clean_text = "The product arrived on time and the build quality is durable."
        _, is_spam_clean, _ = detect_spam(clean_text)
        self.assertFalse(is_spam_clean)

    def test_priority_determination(self):
        """Test complaint priority escalations."""
        crit_text = "Money deducted twice and support is not responding, refund immediately!"
        prio = determine_priority(crit_text, rating=1, sentiment='negative', emotion='anger')
        self.assertEqual(prio, 'critical')

        low_text = "Great software, everything is working nicely."
        prio_low = determine_priority(low_text, rating=5, sentiment='positive', emotion='joy')
        self.assertEqual(prio_low, 'low')

if __name__ == '__main__':
    unittest.main()
