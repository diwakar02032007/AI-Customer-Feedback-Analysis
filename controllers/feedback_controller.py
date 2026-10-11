import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, abort
from models.feedback_model import FeedbackModel
from models.activity_log_model import ActivityLogModel
from services import run_ai_pipeline
from utils.validators import validate_feedback_input
from utils.decorators import login_required, admin_required
from utils.logger import logger

feedback_bp = Blueprint('feedback', __name__)


@feedback_bp.route('/feedback/submit', methods=['GET', 'POST'])
def submit():
    """Handle feedback submission from customers or guests."""
    user_id = session.get('user_id')
    user_name = session.get('user_name', '')
    user_email = session.get('user_email', '')

    if request.method == 'POST':
        name = request.form.get('customer_name', user_name).strip()
        email = request.form.get('customer_email', user_email).strip().lower()
        rating = request.form.get('rating', '5')
        category = request.form.get('category', 'General')
        feedback_text = request.form.get('feedback_text', '').strip()

        is_valid, errors = validate_feedback_input(name, email, rating, feedback_text, category)
        if not is_valid:
            for err in errors:
                flash(err, 'danger')
            return render_template('customer/feedback_form.html', 
                                   name=name, email=email, rating=rating, 
                                   category=category, feedback_text=feedback_text)

        # Run AI/NLP Analysis Pipeline
        ai_result = run_ai_pipeline(feedback_text, rating=rating, user_category=category)

        feedback_data = {
            'user_id': user_id,
            'customer_name': name,
            'customer_email': email,
            'rating': int(rating),
            'feedback_text': feedback_text,
            'category': ai_result['category'],
            'status': 'spam' if ai_result['is_spam'] else 'new',
            'priority': ai_result['priority'],
            'sentiment': ai_result['sentiment'],
            'sentiment_score': ai_result['sentiment_score'],
            'emotion': ai_result['emotion'],
            'aspect': ai_result['aspect'],
            'aspect_sentiment': ai_result['aspect_sentiment'],
            'spam_probability': ai_result['spam_probability'],
            'is_spam': ai_result['is_spam'],
            'language': ai_result['language'],
            'summary': ai_result['summary'],
            'recommendation': ai_result['recommendation']
        }

        feedback_id = FeedbackModel.create(feedback_data, aspect_breakdown=ai_result.get('aspect_breakdown'))
        logger.info(f"Feedback #{feedback_id} recorded with sentiment={ai_result['sentiment']}, priority={ai_result['priority']}.")

        return render_template('customer/feedback_success.html', feedback=feedback_data, feedback_id=feedback_id)

    return render_template('customer/feedback_form.html', name=user_name, email=user_email)

@feedback_bp.route('/customer/my-feedbacks')
@feedback_bp.route('/feedback/my-feedbacks')
@feedback_bp.route('/feedback/my-feedback')
@login_required
def my_feedbacks():
    """Customer view of their personal feedback history."""
    user_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    feedbacks_data = FeedbackModel.get_by_user_id(user_id, page=page, per_page=10)
    return render_template('customer/my_feedback.html', data=feedbacks_data)

@feedback_bp.route('/admin/feedbacks')
@admin_required
def admin_feedbacks():
    """Admin feedback management table with multi-criteria filters and pagination."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    sentiment = request.args.get('sentiment', 'all')
    category = request.args.get('category', 'all')
    priority = request.args.get('priority', 'all')
    status = request.args.get('status', 'all')
    rating = request.args.get('rating', 'all')
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'DESC')

    data = FeedbackModel.get_all(
        page=page,
        per_page=10,
        search=search,
        sentiment=sentiment,
        category=category,
        priority=priority,
        status=status,
        rating=rating,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return render_template(
        'admin/feedbacks.html',
        data=data,
        search=search,
        sentiment=sentiment,
        category=category,
        priority=priority,
        status=status,
        rating=rating,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order
    )

@feedback_bp.route('/admin/feedbacks/import', methods=['POST'])
@admin_required
def admin_import_csv():
    """Import customer feedback dataset from CSV with validation and duplicate detection."""
    if 'csv_file' not in request.files:
        flash('No CSV file selected for import.', 'warning')
        return redirect(url_for('feedback.admin_feedbacks'))

    file = request.files['csv_file']
    if not file or not file.filename:
        flash('Please select a valid CSV file.', 'warning')
        return redirect(url_for('feedback.admin_feedbacks'))

    if not file.filename.lower().endswith('.csv'):
        flash('Invalid file format. Only .csv files are supported.', 'danger')
        return redirect(url_for('feedback.admin_feedbacks'))

    # Check file size (max 5 MB)
    file_bytes = file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        flash('CSV file exceeds 5MB size limit.', 'danger')
        return redirect(url_for('feedback.admin_feedbacks'))

    try:
        # Decode CSV content safely
        stream = io.StringIO(file_bytes.decode('utf-8-sig', errors='replace'))
        reader = csv.DictReader(stream)

        # Normalize header keys to lowercase trimmed
        if not reader.fieldnames:
            flash('Uploaded CSV file is empty.', 'warning')
            return redirect(url_for('feedback.admin_feedbacks'))

        imported_count = 0
        duplicate_count = 0
        skipped_count = 0

        for row in reader:
            # Map case-insensitive columns
            normalized_row = {k.strip().lower(): (v or '').strip() for k, v in row.items() if k}
            
            feedback_text = normalized_row.get('feedback_text') or normalized_row.get('feedback') or normalized_row.get('comment') or normalized_row.get('review') or ''
            if not feedback_text or len(feedback_text) < 3:
                skipped_count += 1
                continue

            customer_name = normalized_row.get('customer_name') or normalized_row.get('name') or 'Anonymous Customer'
            customer_email = normalized_row.get('customer_email') or normalized_row.get('email') or 'customer@import.local'
            category = normalized_row.get('category') or 'General'
            
            try:
                rating = int(normalized_row.get('rating', 5))
                if rating < 1 or rating > 5:
                    rating = 5
            except (ValueError, TypeError):
                rating = 5

            # Duplicate Check (Feature I)
            is_dup = FeedbackModel.check_duplicate(feedback_text, customer_email)
            if is_dup:
                duplicate_count += 1
                continue

            # Run AI Analysis Pipeline
            ai_result = run_ai_pipeline(feedback_text, rating=rating, user_category=category)

            feedback_data = {
                'user_id': None,
                'customer_name': customer_name,
                'customer_email': customer_email,
                'rating': rating,
                'feedback_text': feedback_text,
                'category': ai_result['category'],
                'status': 'spam' if ai_result['is_spam'] else 'new',
                'priority': ai_result['priority'],
                'sentiment': ai_result['sentiment'],
                'sentiment_score': ai_result['sentiment_score'],
                'emotion': ai_result['emotion'],
                'aspect': ai_result['aspect'],
                'aspect_sentiment': ai_result['aspect_sentiment'],
                'spam_probability': ai_result['spam_probability'],
                'is_spam': ai_result['is_spam'],
                'language': ai_result['language'],
                'summary': ai_result['summary'],
                'recommendation': ai_result['recommendation']
            }

            FeedbackModel.create(feedback_data, aspect_breakdown=ai_result.get('aspect_breakdown'))
            imported_count += 1

        # Audit Log (Feature L)
        user_id = session.get('user_id')
        ActivityLogModel.log(
            action='CSV_IMPORT',
            details=f"Imported {imported_count} feedbacks from '{file.filename}'. Skipped {duplicate_count} duplicates and {skipped_count} invalid rows.",
            user_id=user_id,
            ip_address=request.remote_addr
        )

        flash(f"CSV Import Complete: {imported_count} feedback records imported, {duplicate_count} duplicates skipped.", 'success')

    except Exception as e:
        logger.error(f"Error processing CSV import: {e}")
        flash(f"Error parsing CSV file: {str(e)}", 'danger')

    return redirect(url_for('feedback.admin_feedbacks'))

@feedback_bp.route('/admin/feedbacks/<int:feedback_id>')
@feedback_bp.route('/admin/feedback/<int:feedback_id>')
@admin_required
def admin_feedback_detail(feedback_id):
    """View complete feedback detail and AI diagnostics."""
    feedback = FeedbackModel.get_by_id(feedback_id)
    if not feedback:
        flash('Feedback record not found.', 'warning')
        return redirect(url_for('feedback.admin_feedbacks'))

    aspects = FeedbackModel.get_aspects(feedback_id)
    
    # Return JSON if requested by AJAX modal/drawer
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('format') == 'json':
        return jsonify({
            'feedback': feedback,
            'aspects': aspects
        })

    return render_template('admin/feedback_details.html', feedback=feedback, aspects=aspects)

@feedback_bp.route('/admin/feedbacks/<int:feedback_id>/update', methods=['POST'])
@admin_required
def admin_update_feedback(feedback_id):
    """Update feedback status, admin resolution notes, or priority."""
    status = request.form.get('status')
    priority = request.form.get('priority')
    admin_notes = request.form.get('admin_notes', '').strip()

    FeedbackModel.update_status(feedback_id, status=status, admin_notes=admin_notes, priority=priority)

    # Audit Log (Feature L)
    ActivityLogModel.log(
        action='FEEDBACK_UPDATE',
        details=f"Updated feedback #{feedback_id}: status='{status}', priority='{priority}'",
        user_id=session.get('user_id'),
        ip_address=request.remote_addr
    )

    flash(f'Feedback #{feedback_id} updated successfully.', 'success')
    return redirect(url_for('feedback.admin_feedback_detail', feedback_id=feedback_id))

@feedback_bp.route('/admin/feedbacks/<int:feedback_id>/delete', methods=['POST'])
@admin_required
def admin_delete_feedback(feedback_id):
    """Delete a feedback record."""
    FeedbackModel.delete(feedback_id)

    # Audit Log (Feature L)
    ActivityLogModel.log(
        action='FEEDBACK_DELETE',
        details=f"Deleted feedback #{feedback_id}",
        user_id=session.get('user_id'),
        ip_address=request.remote_addr
    )

    flash(f'Feedback #{feedback_id} deleted successfully.', 'info')
    return redirect(url_for('feedback.admin_feedbacks'))


@feedback_bp.route('/api/analyze-live', methods=['POST'])
def analyze_live():
    """Live interactive AI feedback analysis API for instantaneous UI preview."""
    data = request.get_json() or {}
    text = data.get('text', '').strip()
    rating = data.get('rating', 5)
    category = data.get('category', 'General')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    result = run_ai_pipeline(text, rating=rating, user_category=category)
    return jsonify(result)
