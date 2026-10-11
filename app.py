import os
from flask import Flask, render_template, session
from config import config_by_name, BASE_DIR
from database.db import close_db, init_db
from controllers import (
    auth_bp, feedback_bp, dashboard_bp, customer_bp,
    analysis_bp, report_bp, profile_bp
)
from utils.helpers import (
    format_datetime, format_date, get_sentiment_badge_class,
    get_priority_badge_class, get_status_badge_class, get_emotion_icon
)
from utils.logger import logger
from ml.predict import load_models

def create_app(config_name=None):
    """Application factory for Flask MVC architecture."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    
    # Load configuration
    cfg = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(cfg)
    app.config['BASE_DIR'] = BASE_DIR

    # Ensure required runtime directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['REPORTS_DIR'], exist_ok=True)
    os.makedirs(app.config['EXPORTS_DIR'], exist_ok=True)
    os.makedirs(app.config['ML_MODELS_DIR'], exist_ok=True)

    # Register Teardown
    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(customer_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(feedback_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(profile_bp)

    # Register Custom Template Filters
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['sentiment_badge'] = get_sentiment_badge_class
    app.jinja_env.filters['priority_badge'] = get_priority_badge_class
    app.jinja_env.filters['status_badge'] = get_status_badge_class
    app.jinja_env.filters['emotion_icon'] = get_emotion_icon

    # Global Context Processor
    @app.context_processor
    def inject_global_data():
        is_admin = session.get('user_role') == 'admin'
        unread_alerts = []
        if is_admin:
            try:
                from models.analysis_model import AnalysisModel
                unread_alerts = AnalysisModel.get_recent_alerts(limit=5)
            except Exception:
                unread_alerts = []

        return {
            'current_user': {
                'id': session.get('user_id'),
                'name': session.get('user_name'),
                'email': session.get('user_email'),
                'role': session.get('user_role')
            },
            'is_authenticated': 'user_id' in session,
            'is_admin': is_admin,
            'header_alerts': unread_alerts,
            'header_alert_count': len(unread_alerts)
        }


    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_code=404, error_message="Page Not Found"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"Internal server error: {e}")
        return render_template('base.html', error_code=500, error_message="Internal Server Error"), 500

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', error_code=403, error_message="Access Forbidden"), 403

    # Initialize Database Schema & Models on Startup
    with app.app_context():
        try:
            init_db(app, seed=True)
        except Exception as e:
            logger.warning(f"Database initialization warning: {e}")

        try:
            load_models()
        except Exception as e:
            logger.warning(f"ML models initial load warning: {e}")

    logger.info("Flask application initialized successfully.")
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)
