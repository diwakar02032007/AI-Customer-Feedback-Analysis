from database.db import execute_query
from utils.logger import logger

class AnalysisModel:
    @staticmethod
    def get_dashboard_kpis():
        """Compute all primary KPI metrics for Admin Dashboard."""
        query = """
            SELECT 
                COUNT(*) as total_feedback,
                SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive_feedback,
                SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral_feedback,
                SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_feedback,
                AVG(rating) as avg_rating,
                SUM(CASE WHEN priority IN ('high', 'critical') THEN 1 ELSE 0 END) as high_priority_complaints,
                SUM(CASE WHEN is_spam = 1 THEN 1 ELSE 0 END) as spam_count
            FROM feedbacks
        """
        res = execute_query(query, fetch='one')
        if not res:
            return {
                'total_feedback': 0,
                'positive_feedback': 0,
                'neutral_feedback': 0,
                'negative_feedback': 0,
                'avg_rating': 0.0,
                'high_priority_complaints': 0,
                'spam_count': 0,
                'csat_score': 0.0,
                'nps_score': 0.0
            }

        total = res.get('total_feedback') or 0
        positive = res.get('positive_feedback') or 0
        neutral = res.get('neutral_feedback') or 0
        negative = res.get('negative_feedback') or 0
        avg_rating = round(float(res.get('avg_rating') or 0), 2)
        high_prio = res.get('high_priority_complaints') or 0
        spam_cnt = res.get('spam_count') or 0

        # CSAT: % of 4 & 5 star ratings
        csat_query = "SELECT COUNT(*) as csat_positive FROM feedbacks WHERE rating >= 4"
        csat_res = execute_query(csat_query, fetch='one')
        csat_pos = csat_res['csat_positive'] if csat_res else 0
        csat_score = round((csat_pos / total * 100), 1) if total > 0 else 0.0

        # NPS Estimate: (% Promoters [rating 5] - % Detractors [rating 1,2])
        promoters = execute_query("SELECT COUNT(*) as p FROM feedbacks WHERE rating = 5", fetch='one')['p'] if total else 0
        detractors = execute_query("SELECT COUNT(*) as d FROM feedbacks WHERE rating IN (1, 2)", fetch='one')['d'] if total else 0
        nps_score = round(((promoters - detractors) / total * 100), 1) if total > 0 else 0.0

        return {
            'total_feedback': total,
            'positive_feedback': positive,
            'neutral_feedback': neutral,
            'negative_feedback': negative,
            'avg_rating': avg_rating,
            'high_priority_complaints': high_prio,
            'spam_count': spam_cnt,
            'csat_score': csat_score,
            'nps_score': nps_score
        }

    @staticmethod
    def get_category_distribution():
        """Retrieve feedback count and avg sentiment grouped by category."""
        query = """
            SELECT 
                category,
                COUNT(*) as count,
                AVG(rating) as avg_rating,
                SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive_count,
                SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative_count
            FROM feedbacks
            GROUP BY category
            ORDER BY count DESC
        """
        return execute_query(query, fetch='all') or []

    @staticmethod
    def get_emotion_distribution():
        """Retrieve feedback counts grouped by detected emotion."""
        query = """
            SELECT 
                emotion,
                COUNT(*) as count
            FROM feedbacks
            GROUP BY emotion
            ORDER BY count DESC
        """
        return execute_query(query, fetch='all') or []

    @staticmethod
    def get_priority_distribution():
        """Retrieve feedback counts grouped by priority."""
        query = """
            SELECT 
                priority,
                COUNT(*) as count
            FROM feedbacks
            GROUP BY priority
            ORDER BY 
                CASE priority 
                    WHEN 'critical' THEN 1 
                    WHEN 'high' THEN 2 
                    WHEN 'medium' THEN 3 
                    WHEN 'low' THEN 4 
                    ELSE 5 
                END
        """
        return execute_query(query, fetch='all') or []

    @staticmethod
    def get_language_distribution():
        """Retrieve distribution across English, Tamil, and Tanglish."""
        query = """
            SELECT 
                language,
                COUNT(*) as count
            FROM feedbacks
            GROUP BY language
            ORDER BY count DESC
        """
        return execute_query(query, fetch='all') or []

    @staticmethod
    def get_sentiment_trends(days=14):
        """Retrieve daily sentiment counts for timeline trend chart."""
        query = """
            SELECT 
                DATE(created_at) as date_val,
                SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive,
                SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral,
                SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative,
                AVG(rating) as avg_rating,
                COUNT(*) as total
            FROM feedbacks
            GROUP BY DATE(created_at)
            ORDER BY date_val ASC
            LIMIT %s
        """
        return execute_query(query, (days,), fetch='all') or []

    @staticmethod
    def get_top_complaint_categories(limit=5):
        """Retrieve categories with highest negative feedback counts."""
        query = """
            SELECT 
                category,
                COUNT(*) as negative_count,
                AVG(rating) as avg_rating
            FROM feedbacks
            WHERE sentiment = 'negative'
            GROUP BY category
            ORDER BY negative_count DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch='all') or []

    @staticmethod
    def get_most_appreciated_aspects(limit=5):
        """Retrieve aspects with highest positive ratings."""
        query = """
            SELECT 
                aspect,
                COUNT(*) as positive_count,
                AVG(sentiment_score) as avg_sentiment
            FROM feedbacks
            WHERE sentiment = 'positive'
            GROUP BY aspect
            ORDER BY positive_count DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch='all') or []

    @staticmethod
    def get_recent_feedbacks(limit=5):
        """Retrieve recent feedbacks for dashboard summary widget."""
        query = """
            SELECT id, customer_name, rating, feedback_text, category, sentiment, priority, created_at, summary, emotion
            FROM feedbacks
            ORDER BY created_at DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch='all') or []

    @staticmethod
    def get_rating_distribution():
        """Retrieve count of feedbacks for each star rating 1-5."""
        query = """
            SELECT rating, COUNT(*) as count
            FROM feedbacks
            GROUP BY rating
            ORDER BY rating ASC
        """
        rows = execute_query(query, fetch='all') or []
        counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in rows:
            val = r.get('rating')
            if val in counts:
                counts[val] = int(r.get('count', 0))
        return [
            {'rating': star, 'label': f"{star} Star{'s' if star > 1 else ''}", 'count': counts[star]}
            for star in range(1, 6)
        ]

    @staticmethod
    def get_aspect_sentiment_distribution():
        """Retrieve top aspects with positive, neutral, negative distribution."""
        query = """
            SELECT 
                aspect,
                COUNT(*) as total_count,
                SUM(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive,
                SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral,
                SUM(CASE WHEN sentiment = 'negative' THEN 1 ELSE 0 END) as negative
            FROM feedbacks
            WHERE aspect IS NOT NULL AND aspect != ''
            GROUP BY aspect
            ORDER BY total_count DESC
            LIMIT 6
        """
        return execute_query(query, fetch='all') or []

    @staticmethod
    def get_high_priority_feedbacks(limit=6):
        """Retrieve open high/critical priority feedback tickets needing immediate action."""
        query = """
            SELECT id, customer_name, customer_email, rating, feedback_text, category, priority, status, created_at, summary, emotion
            FROM feedbacks
            WHERE priority IN ('critical', 'high') AND status != 'resolved'
            ORDER BY 
                CASE priority WHEN 'critical' THEN 1 ELSE 2 END,
                created_at DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch='all') or []

    @staticmethod
    def get_recent_alerts(limit=5):
        """Retrieve real-time escalation alerts for topbar notification dropdown."""
        query = """
            SELECT id, customer_name, category, priority, feedback_text, summary, created_at
            FROM feedbacks
            WHERE priority IN ('critical', 'high')
            ORDER BY created_at DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch='all') or []

    @staticmethod
    def get_actionable_recommendations(limit=4):
        """Synthesize actionable business recommendations from active negative or critical feedbacks."""
        query = """
            SELECT id, category, priority, recommendation, summary, customer_name, created_at
            FROM feedbacks
            WHERE recommendation IS NOT NULL AND recommendation != '' AND sentiment = 'negative'
            ORDER BY 
                CASE priority WHEN 'critical' THEN 1 WHEN 'high' THEN 2 ELSE 3 END,
                created_at DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch='all') or []

