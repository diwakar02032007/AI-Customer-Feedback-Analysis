import os
import sqlite3
import pymysql
from pymysql.cursors import DictCursor
from flask import g, current_app
from utils.logger import logger

def get_db_type():
    """Determine the active database type (mysql or sqlite fallback)."""
    configured_type = current_app.config.get('DB_TYPE', 'mysql').lower()
    return configured_type

def get_mysql_connection():
    """Attempt connecting to MySQL Community Edition server."""
    host = current_app.config.get('DB_HOST', 'localhost')
    port = current_app.config.get('DB_PORT', 3306)
    user = current_app.config.get('DB_USER', 'root')
    password = current_app.config.get('DB_PASSWORD', '')
    database = current_app.config.get('DB_NAME', 'customer_feedback_db')
    
    try:
        # First ensure database exists
        admin_conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4',
            cursorclass=DictCursor,
            connect_timeout=3
        )
        with admin_conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        admin_conn.commit()
        admin_conn.close()

        # Connect to actual database
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=DictCursor,
            connect_timeout=3,
            autocommit=False
        )
        return conn
    except Exception as e:
        logger.warning(f"MySQL connection to {host}:{port}/{database} failed: {e}")
        return None

def get_sqlite_connection():
    """Get connection to local SQLite database as fallback or testing mode."""
    db_path = current_app.config.get('SQLITE_PATH', 'database/app.db')
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    """Get or create database connection for the current request context."""
    if 'db' not in g:
        db_type = get_db_type()
        conn = None
        
        if db_type == 'mysql':
            conn = get_mysql_connection()
            if conn:
                g.db_mode = 'mysql'
            else:
                logger.info("Falling back to local SQLite database engine for local run.")
                conn = get_sqlite_connection()
                g.db_mode = 'sqlite'
        else:
            conn = get_sqlite_connection()
            g.db_mode = 'sqlite'
            
        g.db = conn

    return g.db

def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

def execute_query(query, params=None, fetch=None, commit=False):
    """
    Execute SQL query safely across MySQL or SQLite.
    fetch: 'one', 'all', or None
    commit: True to commit changes (INSERT, UPDATE, DELETE)
    Returns: dict/list of dicts or lastrowid/rowcount
    """
    db = get_db()
    db_mode = getattr(g, 'db_mode', 'mysql')
    params = params or ()

    # Parameter adaptation for SQLite if needed (%s -> ?)
    adapted_query = query
    if db_mode == 'sqlite':
        adapted_query = adapted_query.replace('%s', '?')
        # SQLite compatibility adjustments
        adapted_query = adapted_query.replace('NOW()', "datetime('now', 'localtime')")
        adapted_query = adapted_query.replace('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', 'CURRENT_TIMESTAMP')

    cursor = db.cursor()
    try:
        cursor.execute(adapted_query, params)
        if commit:
            db.commit()
            last_id = getattr(cursor, 'lastrowid', None)
            return last_id

        if fetch == 'one':
            result = cursor.fetchone()
            if result and db_mode == 'sqlite':
                return dict(result)
            return result
        elif fetch == 'all':
            results = cursor.fetchall()
            if results and db_mode == 'sqlite':
                return [dict(row) for row in results]
            return results
        return None
    except Exception as e:
        logger.error(f"Error executing SQL: {query} with params {params}: {e}")
        if commit:
            db.rollback()
        raise e
    finally:
        cursor.close()

def init_db(app=None, seed=True):
    """Initialize database tables and initial seed data."""
    ctx = app.app_context() if app else None
    if ctx:
        ctx.push()

    try:
        db = get_db()
        db_mode = getattr(g, 'db_mode', 'mysql')
        base_dir = current_app.config['BASE_DIR']

        if db_mode == 'mysql':
            schema_file = os.path.join(base_dir, 'database', 'schema.sql')
            seed_file = os.path.join(base_dir, 'database', 'seed_data.sql')

            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()

            with db.cursor() as cursor:
                # Split statements by semicolon
                statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
                for stmt in statements:
                    # Ignore USE and CREATE DATABASE if handled
                    if stmt.upper().startswith('USE ') or stmt.upper().startswith('CREATE DATABASE'):
                        continue
                    cursor.execute(stmt)
            db.commit()
            logger.info("MySQL database schema applied successfully.")

            if seed and os.path.exists(seed_file):
                with open(seed_file, 'r', encoding='utf-8') as f:
                    seed_sql = f.read()
                with db.cursor() as cursor:
                    statements = [stmt.strip() for stmt in seed_sql.split(';') if stmt.strip()]
                    for stmt in statements:
                        if stmt.upper().startswith('USE ') or stmt.upper().startswith('CREATE DATABASE'):
                            continue
                        try:
                            cursor.execute(stmt)
                        except Exception as se:
                            logger.warning(f"Seed statement skipped or already present: {se}")
                db.commit()
                logger.info("MySQL seed data inserted successfully.")

        else:
            # SQLite Table Initialization
            cursor = db.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'customer',
                    phone TEXT,
                    avatar TEXT DEFAULT 'default_avatar.png',
                    bio TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS feedbacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    customer_name TEXT NOT NULL,
                    customer_email TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    feedback_text TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'General',
                    status TEXT NOT NULL DEFAULT 'new',
                    priority TEXT NOT NULL DEFAULT 'low',
                    sentiment TEXT NOT NULL DEFAULT 'neutral',
                    sentiment_score REAL NOT NULL DEFAULT 0.0,
                    emotion TEXT NOT NULL DEFAULT 'neutral',
                    aspect TEXT NOT NULL DEFAULT 'General',
                    aspect_sentiment TEXT NOT NULL DEFAULT 'neutral',
                    spam_probability REAL NOT NULL DEFAULT 0.0,
                    is_spam INTEGER NOT NULL DEFAULT 0,
                    language TEXT NOT NULL DEFAULT 'English',
                    summary TEXT,
                    recommendation TEXT,
                    admin_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS feedback_aspects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    feedback_id INTEGER NOT NULL,
                    aspect_name TEXT NOT NULL,
                    sentiment TEXT NOT NULL DEFAULT 'neutral',
                    confidence REAL NOT NULL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(feedback_id) REFERENCES feedbacks(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_title TEXT NOT NULL,
                    report_type TEXT NOT NULL DEFAULT 'summary',
                    date_from TEXT,
                    date_to TEXT,
                    total_feedbacks INTEGER NOT NULL DEFAULT 0,
                    positive_count INTEGER NOT NULL DEFAULT 0,
                    neutral_count INTEGER NOT NULL DEFAULT 0,
                    negative_count INTEGER NOT NULL DEFAULT 0,
                    avg_rating REAL NOT NULL DEFAULT 0.0,
                    file_path TEXT,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(created_by) REFERENCES users(id) ON DELETE SET NULL
                );

                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    ip_address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
                );
            """)
            db.commit()

            # Seed SQLite if empty
            user_count = cursor.execute("SELECT COUNT(*) as cnt FROM users").fetchone()[0]
            if user_count == 0 and seed:
                # Insert admin and customers
                cursor.execute("""
                    INSERT INTO users (id, name, email, password_hash, role, phone, bio) VALUES
                    (1, 'System Administrator', 'admin@feedbackai.com', 'scrypt:32768:8:1$W3BlMsnI6OmmLmWr$6db9d38c281c41b77d71dc521763f040e5dacc51448f563bedb403c1621f38faefd9c178ef531ae9d112ea8f885a62dd1f06d950eb305eecc1cf404e67e9844a', 'admin', '+91 9876543210', 'Lead operations and feedback analyst.'),
                    (2, 'John Doe', 'john.doe@example.com', 'scrypt:32768:8:1$4HN0YhqgJtRcZGws$673ec000293d55eae8370c789f6e80e7bd00ffc33e9636d91447027fa1eaee247a7b6fbfb25cbd86eb5e8c6870775272ac6c71912c7f8d0716d1b41eb9e3f376', 'customer', '+91 9811122233', 'Verified Enterprise Customer.'),
                    (3, 'Priya Sundaram', 'priya.s@example.com', 'scrypt:32768:8:1$4HN0YhqgJtRcZGws$673ec000293d55eae8370c789f6e80e7bd00ffc33e9636d91447027fa1eaee247a7b6fbfb25cbd86eb5e8c6870775272ac6c71912c7f8d0716d1b41eb9e3f376', 'customer', '+91 9844455566', 'Frequent user from Chennai.');
                """)

                cursor.execute("""
                    INSERT INTO categories (name, description) VALUES
                    ('Product Quality', 'Durability, build, and specifications'),
                    ('Customer Support', 'Help desk responsiveness and agent courtesy'),
                    ('Billing/Pricing', 'Subscriptions, invoices, and pricing'),
                    ('Delivery/Speed', 'Turnaround time, logistics, and tracking'),
                    ('Usability/UI', 'Website/app user interface and UX workflow'),
                    ('General', 'General customer feedback and inquiries');
                """)

                cursor.execute("""
                    INSERT INTO feedbacks 
                    (id, user_id, customer_name, customer_email, rating, feedback_text, category, status, priority, sentiment, sentiment_score, emotion, aspect, aspect_sentiment, spam_probability, is_spam, language, summary, recommendation, admin_notes)
                    VALUES
                    (1, 2, 'John Doe', 'john.doe@example.com', 5, 'The latest update is outstanding! The user interface is so clean, intuitive, and navigation is buttery smooth. Kudos to the engineering team.', 'Usability/UI', 'resolved', 'low', 'positive', 0.92, 'joy', 'UI/UX', 'positive', 0.02, 0, 'English', 'Customer loved the newest UI update highlighting speed and smooth navigation.', 'Document UI design patterns used in this release as best practices for future releases.', 'Shared praise with frontend dev lead.'),
                    (2, 3, 'Priya Sundaram', 'priya.s@example.com', 1, 'Money deducted twice during checkout and still got no confirmation email! Support team is not answering calls. Horrible experience, refund my money immediately!', 'Billing/Pricing', 'under_review', 'critical', 'negative', -0.95, 'anger', 'Pricing', 'negative', 0.05, 0, 'English', 'Double billing during checkout with unresponsive support helpline, customer demanding immediate refund.', 'Initiate instant reconciliation with payment gateway and call customer.', 'Investigating payment gateway log reference #TXN992.'),
                    (3, 2, 'John Doe', 'john.doe@example.com', 4, 'Delivery was super fast within 24 hours. The packaging was neat, but please provide real-time GPS tracking on the mobile app.', 'Delivery/Speed', 'resolved', 'medium', 'positive', 0.75, 'joy', 'Delivery/Speed', 'positive', 0.03, 0, 'English', 'Fast 24-hour delivery appreciated, requested real-time GPS tracking.', 'Prioritize real-time driver tracking in mobile roadmap.', 'Forwarded to logistics squad.'),
                    (4, NULL, 'Karthik Raja', 'karthik.raja@testmail.com', 2, 'App romba slow-va irukku. Login panna 2 minutes aaguthu. Please fix this bug quickly.', 'Usability/UI', 'new', 'high', 'negative', -0.65, 'sadness', 'Features/Performance', 'negative', 0.04, 0, 'Tanglish', 'App takes over 2 minutes to log in and exhibits severe latency.', 'Inspect auth endpoint latency and optimize database index queries.', NULL),
                    (5, NULL, 'Anitha Murugan', 'anitha.m@testmail.com', 5, 'வாடிக்கையாளர் சேவை மிகவும் அருமை. என் பிரச்சனைக்கு உடனடியாக தீர்வு கிடைத்தது. நன்றி!', 'Customer Support', 'resolved', 'low', 'positive', 0.95, 'joy', 'Customer Support', 'positive', 0.01, 0, 'Tamil', 'Customer expressed gratitude for exceptionally swift and helpful support resolution.', 'Reward the support associate on duty for exceptional multilingual customer satisfaction.', 'Handled by agent Sneha.'),
                    (6, 3, 'Priya Sundaram', 'priya.s@example.com', 3, 'Pricing is reasonable compared to competitors, but customer support takes too long to respond to chat tickets. Fair service overall.', 'Customer Support', 'new', 'medium', 'neutral', 0.10, 'neutral', 'Customer Support', 'neutral', 0.02, 0, 'English', 'Good pricing structure, but customer support chat response SLA needs improvement.', 'Implement automated chatbot routing during peak hours.', NULL),
                    (7, NULL, 'Spam Bot', 'freegift247@xyzmarketing.ru', 1, 'CLICK HERE NOW TO WIN FREE 50000 CASH PRIZE $$$ http://spamlink.xyz/win BUY CHEAP BITCOIN FAST', 'General', 'spam', 'low', 'neutral', 0.00, 'neutral', 'General', 'neutral', 0.99, 1, 'English', 'Promotional spam attempt with malicious URLs.', 'Block sender domain and blacklist IP from feedback submission portal.', 'Flagged as spam.'),
                    (8, NULL, 'Suresh Kumar', 'suresh.k@testmail.com', 4, 'Product quality super-ah irukku. Romba nalla build quality. Delivery mattum konjam fast panna nalla irukkum.', 'Product Quality', 'new', 'medium', 'positive', 0.68, 'joy', 'Product Quality', 'positive', 0.03, 0, 'Tanglish', 'Pleased with solid build and product quality, requested faster delivery turnaround.', 'Maintain high quality manufacturing while auditing courier delivery times.', NULL),
                    (9, NULL, 'Meenakshi Raman', 'meenakshi.r@testmail.com', 1, 'பொருளின் தரம் மிக மோசம். இரண்டு நாட்களிலேயே உடைந்துவிட்டது. பணத்தை திருப்பித் தரவும்.', 'Product Quality', 'under_review', 'critical', 'negative', -0.91, 'anger', 'Product Quality', 'negative', 0.02, 0, 'Tamil', 'Product broke within two days of receipt; customer is demanding immediate refund.', 'Process immediate replacement/refund and raise quality alert with OEM vendor.', 'Replacement dispatch pending approval.'),
                    (10, 2, 'John Doe', 'john.doe@example.com', 5, 'Customer support agent Rahul was very courteous and resolved my billing discrepancy in minutes. Amazing service!', 'Customer Support', 'resolved', 'low', 'positive', 0.88, 'joy', 'Customer Support', 'positive', 0.01, 0, 'English', 'Agent Rahul provided swift and courteous resolution for billing discrepancy.', 'Recognize Rahul in weekly team shoutout for exemplary customer care.', 'Resolved with 5-star customer CSAT.');
                """)
                db.commit()
                logger.info("SQLite database schema and seed data created successfully.")

    except Exception as e:
        logger.error(f"Error during init_db: {e}")
        raise e
    finally:
        if ctx:
            ctx.pop()
