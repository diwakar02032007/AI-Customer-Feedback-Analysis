import os
from datetime import timedelta
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ai-customer-feedback-analysis-secret-key-2026')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.environ.get('PERMANENT_SESSION_LIFETIME_DAYS', 7)))
    SESSION_COOKIE_HTTPONLY = os.environ.get('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    
    # Database Configuration
    DB_TYPE = os.environ.get('DB_TYPE', 'mysql')  # 'mysql' or 'sqlite'
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'customer_feedback_db')
    
    # SQLite Fallback / Dev Path
    SQLITE_PATH = os.path.join(BASE_DIR, 'database', 'app.db')

    # File Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'csv'}

    # ML & NLP Paths
    ML_MODELS_DIR = os.path.join(BASE_DIR, 'ml', 'trained_models')
    DATASETS_DIR = os.path.join(BASE_DIR, 'ml', 'datasets')
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
    EXPORTS_DIR = os.path.join(BASE_DIR, 'reports', 'exports')
    
    # Ollama LLM Configuration (Local / Free)
    OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3')
    OLLAMA_TIMEOUT = int(os.environ.get('OLLAMA_TIMEOUT', 4))  # Fast timeout for fallback

    # Pagination & Display Defaults
    ITEMS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    DB_TYPE = 'sqlite'
    SQLITE_PATH = os.path.join(BASE_DIR, 'database', 'test.db')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
