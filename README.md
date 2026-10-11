# AI-Powered Customer Feedback Analysis System

An enterprise-ready, multilingual Customer Feedback Analysis web application built with **Flask MVC Architecture**, **MySQL Community Edition**, **Bootstrap 5**, **Chart.js**, and local **Scikit-Learn NLP / Local Ollama**.

Designed to process and analyze feedback submitted in **English**, **தமிழ் (Tamil)**, and **Tanglish** (phonetic Tamil in Latin script).

---

## 🌟 Key Features

1. **Multilingual NLP Engine**:
   - Automated language detection (**English**, **Tamil**, and **Tanglish**).
   - High-accuracy sentiment analysis (`positive`, `neutral`, `negative`) with numerical polarity score (`-1.0` to `+1.0`).
   - 6-state emotion detection (`Joy`, `Sadness`, `Anger`, `Fear`, `Surprise`, `Neutral`).
   - Aspect-Based Sentiment Analysis (ABSA) for `UI/UX`, `Customer Support`, `Pricing`, `Delivery/Speed`, and `Product Quality`.
   - Category classification across departments.
   - Intelligent complaint priority triage (`Critical`, `High`, `Medium`, `Low`).
   - Spam and fake submission detection (`spam_probability` score).
   - Executive 1-sentence feedback summarization.
   - Actionable AI business recommendations for management.
   - Optional local Ollama LLM integration (`http://localhost:11434`) with zero-blocking offline fallback.

2. **Customer Experience Portal**:
   - Modern, responsive landing page with feature highlights.
   - 5-Star interactive rating widget and instant validation.
   - Real-time **"Preview AI Analysis"** button for live pipeline testing.
   - Quick one-click sample presets (English praise, English complaint, Tamil feedback, Tanglish feedback).
   - Instant AI diagnostics breakdown after submission.
   - Personal feedback history tracking with review statuses.
   - Customer profile management and password updating.

3. **Executive Admin Dashboard & Analytics**:
   - Modern light theme SaaS dashboard with sidebar navigation.
   - Real-time KPI Cards: Total Feedback, Positive, Neutral, Negative, Average Rating, and High/Critical Complaints.
   - Operational Metrics: Customer Satisfaction Score (**CSAT** %) and Net Promoter Score (**NPS**).
   - Interactive Chart.js visual telemetry:
     - 14-day sentiment trend timeline (Line chart).
     - Departmental category volume (Bar chart).
     - Emotion breakdown (Doughnut chart).
     - Priority severity tickets (Bar chart).
     - Language distribution (Pie chart).
   - Top complaint categories and most appreciated aspects tables.
   - Interactive Feedback Detail Modal & Drawer with full AI diagnostics.
   - Advanced feedback table with multi-criteria search, filters (Sentiment, Category, Priority, Status), sorting, and pagination.
   - Status updates, priority adjustment, and internal resolution notes.
   - Point-in-time executive report snapshot generator.
   - Complete raw dataset **CSV Export**.

---

## 🏗️ Architecture & Project Structure

The project strictly follows the **Flask MVC (Model-View-Controller)** pattern:

```
AI-Customer-Feedback-Analysis/
│
├── app.py                      # Application Factory & Configuration
├── config.py                   # Environment & Database Configuration
├── requirements.txt            # Python Dependencies
├── .env                        # Local Environment Variables
├── .gitignore                  # Git Ignore Rules
├── README.md                   # System Documentation & Run Guide
├── run.py                      # Development Server Launcher
│
├── database/                   # Database Layer
│   ├── db.py                   # DB Connection & Auto-Migration Layer
│   ├── schema.sql              # MySQL Schema (Tables, Foreign Keys, Indexes)
│   └── seed_data.sql           # Multilingual Seed Data (English, Tamil, Tanglish)
│
├── models/                     # Business Logic & Data Models
│   ├── user_model.py           # User Authentication & RBAC Model
│   ├── feedback_model.py       # Feedback CRUD, Filters, & Aspects
│   ├── analysis_model.py       # KPI Telemetry, Trends, & Aggregations
│   └── report_model.py         # Executive Reports History Model
│
├── controllers/                # Flask Blueprints (Controllers)
│   ├── auth_controller.py      # Login, Register, Logout, Password Reset
│   ├── feedback_controller.py  # Submission & Admin Feedback Management
│   ├── dashboard_controller.py # Admin Dashboard & Customer Landing
│   ├── analysis_controller.py  # Deep-Dive Analytics & Chart.js API
│   ├── report_controller.py    # Report Generation & CSV Export
│   └── profile_controller.py   # User Profile & Security Settings
│
├── services/                   # AI & NLP Processing Services
│   ├── language_service.py     # English / Tamil / Tanglish Detector
│   ├── spam_detection_service.py# Spam Probability & Bot Filtering
│   ├── sentiment_service.py    # Multilingual Sentiment Scoring
│   ├── emotion_service.py      # Emotion Classification
│   ├── category_service.py     # Departmental Classification
│   ├── aspect_service.py       # Aspect-Based Sentiment Analysis
│   ├── priority_service.py     # Automated Complaint Priority
│   ├── summarization_service.py# One-Sentence Executive Summarizer
│   ├── recommendation_service.py# AI Business Recommendations
│   └── ollama_service.py       # Local Ollama LLM Client & Fallback
│
├── ml/                         # Machine Learning Pipeline
│   ├── datasets/               # Multilingual Datasets
│   │   ├── training_data.csv   # Training dataset with labels
│   │   └── feedback_dataset.csv# Evaluation dataset
│   ├── trained_models/         # Serialized Scikit-Learn Models (.pkl)
│   ├── preprocessing.py        # Text Normalization & Cleaning
│   ├── feature_extraction.py   # TF-IDF Vectorizer
│   ├── train_model.py          # Model Training Script
│   └── predict.py              # Real-Time Predictor
│
├── templates/                  # Jinja2 Views
│   ├── base.html               # Main SaaS Layout (Dual Navigation)
│   ├── admin/                  # Admin Views (Dashboard, Feedbacks, Analytics, Reports, Users)
│   ├── customer/               # Customer Views (Home, Feedback Form, Success, History)
│   ├── auth/                   # Auth Views (Login, Register, Forgot Password)
│   └── profile/                # Profile View
│
├── static/                     # Static Assets
│   ├── css/                    # Custom Styles (style.css, dashboard.css, auth.css, responsive.css)
│   ├── js/                     # Client Scripts (main.js, feedback.js, charts.js, dashboard.js, analytics.js)
│   └── images/                 # System Graphics (logo.png, hero.png)
│
├── utils/                      # Utilities & Helpers
│   ├── decorators.py           # Route Decorators (@admin_required, @login_required)
│   ├── validators.py           # Input Validation & Sanitization
│   ├── helpers.py              # Formatting & Pagination Helpers
│   ├── text_utils.py           # Tamil/Tanglish Text Processing
│   └── logger.py               # Structured Logging Utility
│
├── reports/                    # Reports Directory
│   ├── exports/                # CSV Export Storage
│   └── generated/              # Saved HTML Snapshot Reports
│
└── tests/                      # Automated Test Suite (21 Tests)
    ├── test_auth.py            # Authentication & RBAC Tests
    ├── test_feedback.py        # Feedback Submission & Live Preview Tests
    ├── test_sentiment.py       # Multilingual NLP & Sentiment Tests
    ├── test_analysis.py        # KPIs, Trends, & Analytics Tests
    └── test_dashboard.py       # Dashboard & CSV Export Tests
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask (MVC Architecture)
- **Database**: MySQL Community Edition (PyMySQL driver) with zero-config auto-fallback for immediate out-of-the-box local testing
- **Frontend**: HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons, Chart.js 4.4
- **AI & ML**: Scikit-Learn (TF-IDF + Classifiers), Multilingual Lexicons, Local Ollama LLM integration (no paid APIs)
- **Security**: Werkzeug Scrypt password hashing, session cookies, parameterized queries, input sanitization

---

## 🚀 How to Run the Project in VS Code

### Step 1: Open the Project in VS Code
Open the project directory in VS Code:
```powershell
cd "c:\Users\DIWAKAR A M\OneDrive\Pictures\Documents\AI-CUSTOMER FEEDBACK-ANALYSIS\AI-Customer-Feedback-Analysis"
```

### Step 2: Install Python Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Configure Database (.env)
The application is pre-configured in `.env`. By default, it connects to MySQL:
```env
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=customer_feedback_db
```

> **Note**: If your local MySQL service is running, import `database/schema.sql` and `database/seed_data.sql`:
> ```sql
> mysql -u root -p < database/schema.sql
> mysql -u root -p < database/seed_data.sql
> ```
> If MySQL is not running yet, the application automatically initializes an embedded fallback database (`database/app.db`) with full schema and seed data so you can test and demonstrate the system immediately without any setup hurdles!

### Step 4: Run the Application
Start the local server by running:
```powershell
python run.py
```

Open your browser and navigate to:
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Default Credentials

### Administrator Account
- **Email**: `admin@feedbackai.com`
- **Password**: `AdminPassword123!`
- **Access**: Full Admin Dashboard, Feedback Inspection, Status Management, Analytics, Reports, CSV Export, User Directory

### Customer Account
- **Email**: `john.doe@example.com`
- **Password**: `Customer123!`
- **Access**: Submit Feedback, View Personal Submission History, Edit Profile

*(Quick Login buttons are provided on the login page to fill these credentials in one click.)*

---

## 🧪 Running Automated Tests

Run the complete test suite:
```powershell
python -m unittest discover tests
```
All **21 unit and integration tests** verify authentication, multilingual NLP, emotion extraction, priority triage, feedback submission, and analytics endpoints.
