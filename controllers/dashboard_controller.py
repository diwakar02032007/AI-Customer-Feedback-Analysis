from flask import Blueprint, render_template, session, redirect, url_for, request
from models.analysis_model import AnalysisModel
from models.user_model import UserModel
from utils.decorators import admin_required

dashboard_bp = Blueprint('dashboard', __name__)
customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
@customer_bp.route('/home')
def home():
    """Customer-facing landing and home page."""
    return render_template('customer/home.html')

@dashboard_bp.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Main modern SaaS Admin Dashboard."""
    kpis = AnalysisModel.get_dashboard_kpis()
    category_dist = AnalysisModel.get_category_distribution()
    emotion_dist = AnalysisModel.get_emotion_distribution()
    priority_dist = AnalysisModel.get_priority_distribution()
    top_complaints = AnalysisModel.get_top_complaint_categories(limit=5)
    top_aspects = AnalysisModel.get_most_appreciated_aspects(limit=5)
    recent_feedbacks = AnalysisModel.get_recent_feedbacks(limit=6)
    rating_dist = AnalysisModel.get_rating_distribution()
    aspect_dist = AnalysisModel.get_aspect_sentiment_distribution()
    high_priority_feedbacks = AnalysisModel.get_high_priority_feedbacks(limit=5)
    recommendations = AnalysisModel.get_actionable_recommendations(limit=4)

    return render_template(
        'admin/dashboard.html',
        kpis=kpis,
        category_dist=category_dist,
        emotion_dist=emotion_dist,
        priority_dist=priority_dist,
        top_complaints=top_complaints,
        top_aspects=top_aspects,
        recent_feedbacks=recent_feedbacks,
        rating_dist=rating_dist,
        aspect_dist=aspect_dist,
        high_priority_feedbacks=high_priority_feedbacks,
        recommendations=recommendations
    )


@dashboard_bp.route('/admin/users')
@admin_required
def admin_users():
    """List registered users with roles and timestamps."""
    page = request.args.get('page', 1, type=int)
    users_data = UserModel.get_all(page=page, per_page=10)
    return render_template('admin/users.html', data=users_data)
