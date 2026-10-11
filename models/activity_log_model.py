from database.db import execute_query
from utils.logger import logger

class ActivityLogModel:
    @staticmethod
    def log(action, details=None, user_id=None, ip_address=None, **kwargs):
        """Record an administrative audit log entry in the activity_logs table."""
        try:
            query = """
                INSERT INTO activity_logs (user_id, action, details, ip_address)
                VALUES (%s, %s, %s, %s)
            """
            return execute_query(query, (user_id, action, details, ip_address or '127.0.0.1'), commit=True)
        except Exception as e:
            logger.warning(f"Failed to record activity log: {e}")
            return None

    @staticmethod
    def get_recent(limit=10):
        """Retrieve recent audit logs with user info."""
        query = """
            SELECT a.id, a.user_id, a.action, a.details, a.ip_address, a.created_at, u.name as user_name, u.email as user_email
            FROM activity_logs a
            LEFT JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
            LIMIT %s
        """
        return execute_query(query, (limit,), fetch='all') or []
