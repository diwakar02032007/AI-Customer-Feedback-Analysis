from database.db import execute_query
from utils.logger import logger

class FeedbackModel:
    @staticmethod
    def create(data, aspect_breakdown=None):
        """Insert analyzed feedback and associated aspect breakdown."""
        query = """
            INSERT INTO feedbacks (
                user_id, customer_name, customer_email, rating, feedback_text,
                category, status, priority, sentiment, sentiment_score,
                emotion, aspect, aspect_sentiment, spam_probability, is_spam,
                language, summary, recommendation
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s
            )
        """
        params = (
            data.get('user_id'),
            data.get('customer_name'),
            data.get('customer_email'),
            int(data.get('rating', 3)),
            data.get('feedback_text'),
            data.get('category', 'General'),
            data.get('status', 'new'),
            data.get('priority', 'low'),
            data.get('sentiment', 'neutral'),
            float(data.get('sentiment_score', 0.0)),
            data.get('emotion', 'neutral'),
            data.get('aspect', 'General'),
            data.get('aspect_sentiment', 'neutral'),
            float(data.get('spam_probability', 0.0)),
            1 if data.get('is_spam') else 0,
            data.get('language', 'English'),
            data.get('summary'),
            data.get('recommendation')
        )
        feedback_id = execute_query(query, params, commit=True)

        # Insert aspect breakdowns if provided
        if feedback_id and aspect_breakdown:
            for item in aspect_breakdown:
                aspect_query = """
                    INSERT INTO feedback_aspects (feedback_id, aspect_name, sentiment, confidence)
                    VALUES (%s, %s, %s, %s)
                """
                execute_query(aspect_query, (
                    feedback_id,
                    item.get('aspect_name', 'General'),
                    item.get('sentiment', 'neutral'),
                    float(item.get('confidence', 0.8))
                ), commit=True)

        return feedback_id

    @staticmethod
    def get_by_id(feedback_id):
        """Fetch single feedback by ID with detailed info."""
        query = "SELECT * FROM feedbacks WHERE id = %s"
        return execute_query(query, (feedback_id,), fetch='one')

    @staticmethod
    def get_aspects(feedback_id):
        """Fetch all granular aspect records for a feedback."""
        query = "SELECT * FROM feedback_aspects WHERE feedback_id = %s"
        return execute_query(query, (feedback_id,), fetch='all') or []

    @staticmethod
    def get_all(page=1, per_page=10, search=None, sentiment=None, category=None, priority=None, status=None, rating=None, date_from=None, date_to=None, sort_by='created_at', sort_order='DESC'):
        """Query feedbacks with comprehensive multi-criteria filters, date ranges, rating, sorting, and pagination."""
        conditions = []
        params = []

        if search:
            conditions.append("(customer_name LIKE %s OR customer_email LIKE %s OR feedback_text LIKE %s OR summary LIKE %s)")
            wildcard = f"%{search.strip()}%"
            params.extend([wildcard, wildcard, wildcard, wildcard])

        if sentiment and sentiment != 'all':
            conditions.append("sentiment = %s")
            params.append(sentiment)

        if category and category != 'all':
            conditions.append("category = %s")
            params.append(category)

        if priority and priority != 'all':
            conditions.append("priority = %s")
            params.append(priority)

        if status and status != 'all':
            conditions.append("status = %s")
            params.append(status)

        if rating and str(rating) != 'all':
            try:
                r_val = int(rating)
                conditions.append("rating = %s")
                params.append(r_val)
            except (ValueError, TypeError):
                pass

        if date_from and str(date_from).strip():
            conditions.append("DATE(created_at) >= %s")
            params.append(str(date_from).strip())

        if date_to and str(date_to).strip():
            conditions.append("DATE(created_at) <= %s")
            params.append(str(date_to).strip())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Safe sorting column check
        allowed_sort = {'created_at', 'rating', 'sentiment_score', 'priority', 'status'}
        if sort_by not in allowed_sort:
            sort_by = 'created_at'
        order = 'ASC' if sort_order.upper() == 'ASC' else 'DESC'

        # Total count query
        count_query = f"SELECT COUNT(*) as cnt FROM feedbacks {where_clause}"
        total_res = execute_query(count_query, tuple(params), fetch='one')
        total = total_res['cnt'] if total_res else 0

        # Paginated fetch
        total_pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        fetch_query = f"""
            SELECT * FROM feedbacks 
            {where_clause} 
            ORDER BY {sort_by} {order} 
            LIMIT %s OFFSET %s
        """
        fetch_params = tuple(params + [per_page, offset])
        items = execute_query(fetch_query, fetch_params, fetch='all') or []

        return {
            'items': items,
            'feedbacks': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'prev_num': page - 1,
            'has_next': page < total_pages,
            'next_num': page + 1
        }

    @staticmethod
    def get_by_user_id(user_id, page=1, per_page=10):
        """Fetch feedbacks submitted by specific registered user."""
        count_query = "SELECT COUNT(*) as cnt FROM feedbacks WHERE user_id = %s"
        total_res = execute_query(count_query, (user_id,), fetch='one')
        total = total_res['cnt'] if total_res else 0

        total_pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page
        query = """
            SELECT * FROM feedbacks 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        items = execute_query(query, (user_id, per_page, offset), fetch='all') or []

        return {
            'items': items,
            'feedbacks': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'prev_num': page - 1,
            'has_next': page < total_pages,
            'next_num': page + 1
        }

    @staticmethod
    def check_duplicate(feedback_text, customer_email=None):
        """Check if identical or duplicate customer feedback exists in the system."""
        text = (feedback_text or '').strip()
        if not text:
            return None
        query = "SELECT id, customer_name, customer_email, created_at FROM feedbacks WHERE LOWER(TRIM(feedback_text)) = %s"
        params = [text.lower()]
        if customer_email:
            query += " OR (LOWER(TRIM(customer_email)) = %s AND LOWER(TRIM(feedback_text)) = %s)"
            params.extend([customer_email.strip().lower(), text.lower()])
        query += " LIMIT 1"
        return execute_query(query, tuple(params), fetch='one')

    @staticmethod
    def update_status(feedback_id, status, admin_notes=None, priority=None):
        """Update feedback status, priority, and internal admin notes."""
        if priority:
            query = "UPDATE feedbacks SET status = %s, admin_notes = %s, priority = %s WHERE id = %s"
            params = (status, admin_notes, priority, feedback_id)
        else:
            query = "UPDATE feedbacks SET status = %s, admin_notes = %s WHERE id = %s"
            params = (status, admin_notes, feedback_id)
        return execute_query(query, params, commit=True)

    @staticmethod
    def delete(feedback_id):
        """Delete feedback record."""
        query = "DELETE FROM feedbacks WHERE id = %s"
        return execute_query(query, (feedback_id,), commit=True)

