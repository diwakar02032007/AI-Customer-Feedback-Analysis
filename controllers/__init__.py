from controllers.auth_controller import auth_bp
from controllers.feedback_controller import feedback_bp
from controllers.dashboard_controller import dashboard_bp, customer_bp
from controllers.analysis_controller import analysis_bp
from controllers.report_controller import report_bp
from controllers.profile_controller import profile_bp

__all__ = [
    'auth_bp',
    'feedback_bp',
    'dashboard_bp',
    'customer_bp',
    'analysis_bp',
    'report_bp',
    'profile_bp'
]
