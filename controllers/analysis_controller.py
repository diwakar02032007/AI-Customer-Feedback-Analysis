from flask import Blueprint, render_template, jsonify, request
from models.analysis_model import AnalysisModel
from utils.decorators import admin_required

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/admin/analytics')
@admin_required
def analytics_view():
    """Detailed analytics dashboard with deep-dive visual metrics."""
    days = request.args.get('days', 14, type=int)
    kpis = AnalysisModel.get_dashboard_kpis()
    trends = AnalysisModel.get_sentiment_trends(days=days)
    cat_dist = AnalysisModel.get_category_distribution()
    emotion_dist = AnalysisModel.get_emotion_distribution()
    prio_dist = AnalysisModel.get_priority_distribution()
    lang_dist = AnalysisModel.get_language_distribution()
    top_aspects = AnalysisModel.get_most_appreciated_aspects(limit=5)
    top_complaints = AnalysisModel.get_top_complaint_categories(limit=5)
    rating_dist = AnalysisModel.get_rating_distribution()
    aspect_dist = AnalysisModel.get_aspect_sentiment_distribution()

    return render_template(
        'admin/analytics.html',
        kpis=kpis,
        trends=trends,
        category_dist=cat_dist,
        emotion_dist=emotion_dist,
        priority_dist=prio_dist,
        language_dist=lang_dist,
        top_aspects=top_aspects,
        top_complaints=top_complaints,
        rating_dist=rating_dist,
        aspect_dist=aspect_dist,
        selected_days=days
    )

@analysis_bp.route('/admin/insights')
@admin_required
def admin_insights():
    """Dedicated AI Insights and Customer Intelligence page."""
    kpis = AnalysisModel.get_dashboard_kpis()
    top_complaints = AnalysisModel.get_top_complaint_categories(limit=6)
    top_aspects = AnalysisModel.get_most_appreciated_aspects(limit=6)
    trends = AnalysisModel.get_sentiment_trends(days=14)
    recent = AnalysisModel.get_recent_feedbacks(limit=5)
    cat_dist = AnalysisModel.get_category_distribution()
    recommendations = AnalysisModel.get_actionable_recommendations(limit=5)
    high_priority = AnalysisModel.get_high_priority_feedbacks(limit=5)

    return render_template(
        'admin/insights.html',
        kpis=kpis,
        top_complaints=top_complaints,
        top_aspects=top_aspects,
        trends=trends,
        recent=recent,
        category_dist=cat_dist,
        recommendations=recommendations,
        high_priority=high_priority
    )

@analysis_bp.route('/api/analytics-data')
@admin_required
def analytics_data_api():
    """JSON API endpoint returning data formatted for Chart.js charts."""
    days = request.args.get('days', 14, type=int)
    kpis = AnalysisModel.get_dashboard_kpis()
    trends = AnalysisModel.get_sentiment_trends(days=days)
    category_dist = AnalysisModel.get_category_distribution()
    emotion_dist = AnalysisModel.get_emotion_distribution()
    priority_dist = AnalysisModel.get_priority_distribution()
    language_dist = AnalysisModel.get_language_distribution()
    rating_dist = AnalysisModel.get_rating_distribution()
    aspect_dist = AnalysisModel.get_aspect_sentiment_distribution()

    return jsonify({
        'kpis': kpis,
        'trends': {
            'labels': [str(t['date_val']) for t in trends],
            'positive': [int(t['positive']) for t in trends],
            'neutral': [int(t['neutral']) for t in trends],
            'negative': [int(t['negative']) for t in trends],
            'avg_rating': [float(t['avg_rating'] or 0) for t in trends]
        },
        'categories': {
            'labels': [c['category'] for c in category_dist],
            'counts': [int(c['count']) for c in category_dist],
            'ratings': [float(c['avg_rating'] or 0) for c in category_dist]
        },
        'emotions': {
            'labels': [e['emotion'].capitalize() for e in emotion_dist],
            'counts': [int(e['count']) for e in emotion_dist]
        },
        'priorities': {
            'labels': [p['priority'].capitalize() for p in priority_dist],
            'counts': [int(p['count']) for p in priority_dist]
        },
        'languages': {
            'labels': [l['language'] for l in language_dist],
            'counts': [int(l['count']) for l in language_dist]
        },
        'ratings': {
            'labels': [r['label'] for r in rating_dist],
            'counts': [int(r['count']) for r in rating_dist]
        },
        'aspects': {
            'labels': [a['aspect'] for a in aspect_dist],
            'positive': [int(a['positive']) for a in aspect_dist],
            'neutral': [int(a['neutral']) for a in aspect_dist],
            'negative': [int(a['negative']) for a in aspect_dist],
            'counts': [int(a['total_count']) for a in aspect_dist]
        }
    })

