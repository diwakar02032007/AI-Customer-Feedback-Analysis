import os
import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response, send_file, current_app
from models.analysis_model import AnalysisModel
from models.feedback_model import FeedbackModel
from models.report_model import ReportModel
from models.activity_log_model import ActivityLogModel
from utils.decorators import admin_required
from utils.logger import logger

report_bp = Blueprint('report', __name__, url_prefix='/admin/reports')

@report_bp.route('', methods=['GET'])
@report_bp.route('/', methods=['GET'])
@admin_required
def list_reports():
    """List historical reports and executive summaries."""
    page = request.args.get('page', 1, type=int)
    reports_data = ReportModel.get_all(page=page, per_page=10)
    kpis = AnalysisModel.get_dashboard_kpis()
    activity_logs = ActivityLogModel.get_recent(limit=10)
    return render_template('admin/reports.html', data=reports_data, kpis=kpis, activity_logs=activity_logs)


@report_bp.route('/generate', methods=['POST'])
@admin_required
def generate_report():
    """Generate and store an executive summary report snapshot."""
    title = request.form.get('report_title', f"Executive AI Summary - {datetime.now().strftime('%b %d, %Y')}")
    report_type = request.form.get('report_type', 'Executive Summary')
    user_id = session.get('user_id')

    kpis = AnalysisModel.get_dashboard_kpis()
    
    # Create HTML/text snapshot in reports/generated
    reports_dir = current_app.config.get('REPORTS_DIR', 'reports')
    generated_dir = os.path.join(reports_dir, 'generated')
    os.makedirs(generated_dir, exist_ok=True)
    
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"report_{timestamp_str}.html"
    filepath = os.path.join(generated_dir, filename)

    top_complaints = AnalysisModel.get_top_complaint_categories(5)
    top_aspects = AnalysisModel.get_most_appreciated_aspects(5)

    # Simple formatted static snapshot
    report_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 40px; color: #1e293b; }}
            h1 {{ color: #4f46e5; }}
            .kpi-box {{ display: flex; gap: 20px; margin: 30px 0; }}
            .card {{ border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; flex: 1; }}
            .num {{ font-size: 28px; font-weight: bold; color: #0f172a; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div class="kpi-box">
            <div class="card"><div>Total Feedbacks</div><div class="num">{kpis['total_feedback']}</div></div>
            <div class="card"><div>Average Rating</div><div class="num">{kpis['avg_rating']} / 5.0</div></div>
            <div class="card"><div>CSAT Score</div><div class="num">{kpis['csat_score']}%</div></div>
            <div class="card"><div>Positive Ratio</div><div class="num">{kpis['positive_feedback']}</div></div>
            <div class="card"><div>Critical Complaints</div><div class="num">{kpis['high_priority_complaints']}</div></div>
        </div>
        <h2>Key Takeaways</h2>
        <p>This report highlights ongoing customer sentiment and operational priorities across categories.</p>
    </body>
    </html>
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report_html)

    report_id = ReportModel.create(
        title=title,
        report_type=report_type,
        date_from=None,
        date_to=None,
        total=kpis['total_feedback'],
        pos=kpis['positive_feedback'],
        neu=kpis['neutral_feedback'],
        neg=kpis['negative_feedback'],
        avg_rating=kpis['avg_rating'],
        file_path=filename,
        user_id=user_id
    )

    # Audit Log
    ActivityLogModel.log(
        action='REPORT_GENERATE',
        details=f"Generated executive report '{title}' ({report_type})",
        user_id=user_id,
        ip_address=request.remote_addr
    )

    flash(f"Report '{title}' generated successfully.", 'success')
    return redirect(url_for('report.list_reports'))

@report_bp.route('/export-csv')
@admin_required
def export_csv():
    """Export feedback records using currently applied filters as CSV file."""
    search = request.args.get('search', '').strip()
    sentiment = request.args.get('sentiment', 'all')
    category = request.args.get('category', 'all')
    priority = request.args.get('priority', 'all')
    status = request.args.get('status', 'all')
    rating = request.args.get('rating', 'all')
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    # Fetch records matching active criteria
    all_feedbacks_data = FeedbackModel.get_all(
        page=1,
        per_page=10000,
        search=search,
        sentiment=sentiment,
        category=category,
        priority=priority,
        status=status,
        rating=rating,
        date_from=date_from,
        date_to=date_to
    )
    feedbacks = all_feedbacks_data.get('items', [])

    output = io.StringIO()
    writer = csv.writer(output)

    # CSV Header
    writer.writerow([
        'Feedback ID', 'Customer Name', 'Customer Email', 'Rating',
        'Feedback Text', 'Category', 'Status', 'Priority',
        'Sentiment', 'Sentiment Score', 'Emotion', 'Aspect',
        'Spam Probability', 'Is Spam', 'Language', 'Summary',
        'AI Business Recommendation', 'Admin Notes', 'Date Submitted'
    ])

    for f in feedbacks:
        writer.writerow([
            f.get('id'),
            f.get('customer_name'),
            f.get('customer_email'),
            f.get('rating'),
            f.get('feedback_text'),
            f.get('category'),
            f.get('status'),
            f.get('priority'),
            f.get('sentiment'),
            f.get('sentiment_score'),
            f.get('emotion'),
            f.get('aspect'),
            f.get('spam_probability'),
            'Yes' if f.get('is_spam') else 'No',
            f.get('language'),
            f.get('summary'),
            f.get('recommendation'),
            f.get('admin_notes') or '',
            f.get('created_at')
        ])

    output.seek(0)
    filename = f"insightai_feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    # Audit Log
    ActivityLogModel.log(
        action='CSV_EXPORT',
        details=f"Exported {len(feedbacks)} feedback records to CSV (sentiment={sentiment}, category={category}, priority={priority})",
        user_id=session.get('user_id'),
        ip_address=request.remote_addr
    )

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

