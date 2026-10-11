from database.db import execute_query

class ReportModel:
    @staticmethod
    def create(title, report_type, date_from, date_to, total, pos, neu, neg, avg_rating, file_path, user_id=None):
        """Insert report generation audit record."""
        query = """
            INSERT INTO reports (
                report_title, report_type, date_from, date_to,
                total_feedbacks, positive_count, neutral_count, negative_count,
                avg_rating, file_path, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (title, report_type, date_from, date_to, total, pos, neu, neg, avg_rating, file_path, user_id)
        return execute_query(query, params, commit=True)

    @staticmethod
    def get_all(page=1, per_page=10):
        """Fetch paginated reports."""
        count_query = "SELECT COUNT(*) as cnt FROM reports"
        total_res = execute_query(count_query, fetch='one')
        total = total_res['cnt'] if total_res else 0

        offset = (page - 1) * per_page
        query = "SELECT * FROM reports ORDER BY created_at DESC LIMIT %s OFFSET %s"
        items = execute_query(query, (per_page, offset), fetch='all') or []

        total_pages = max(1, (total + per_page - 1) // per_page)
        return {
            'items': items,
            'reports': items,
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
    def get_by_id(report_id):
        """Fetch report by primary key."""
        query = "SELECT * FROM reports WHERE id = %s"
        return execute_query(query, (report_id,), fetch='one')
