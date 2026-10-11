// ========================================================
// InsightAI - Feedback Interactive Controller & Drawer
// ========================================================

document.addEventListener('DOMContentLoaded', function () {
    const feedbackText = document.getElementById('feedbackText');
    const charCounter = document.getElementById('charCount');
    const livePreviewBtn = document.getElementById('livePreviewBtn');
    const previewContainer = document.getElementById('aiLivePreview');
    const ratingInputs = document.querySelectorAll('input[name="rating"]');
    const ratingLabel = document.getElementById('ratingLabel');
    const feedbackForm = document.getElementById('customerFeedbackForm');

    const ratingDescriptions = {
        '1': '1 Star - Highly Dissatisfied',
        '2': '2 Stars - Needs Improvement',
        '3': '3 Stars - Neutral / Average',
        '4': '4 Stars - Satisfied',
        '5': '5 Stars - Delighted / Excellent'
    };

    // Update Rating Text description
    if (ratingInputs.length > 0 && ratingLabel) {
        ratingInputs.forEach(input => {
            input.addEventListener('change', function () {
                ratingLabel.textContent = ratingDescriptions[this.value] || '';
            });
            if (input.checked) {
                ratingLabel.textContent = ratingDescriptions[input.value] || '';
            }
        });
    }

    // Live Character Counter
    if (feedbackText && charCounter) {
        feedbackText.addEventListener('input', function () {
            const count = this.value.length;
            charCounter.textContent = `${count} / 3000`;
            if (count > 2800) {
                charCounter.classList.add('text-danger');
                charCounter.classList.remove('text-muted');
            } else {
                charCounter.classList.remove('text-danger');
                charCounter.classList.add('text-muted');
            }
        });
    }

    // Submit button loading state
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function () {
            const submitBtn = document.getElementById('submitFeedbackBtn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Submitting &amp; Analyzing...';
            }
        });
    }

    // Live Interactive AI Preview
    if (livePreviewBtn && feedbackText && previewContainer) {
        livePreviewBtn.addEventListener('click', async function () {
            const text = feedbackText.value.trim();
            if (text.length < 5) {
                alert('Please enter at least 5 characters to run the AI preview.');
                return;
            }

            const activeRating = document.querySelector('input[name="rating"]:checked');
            const ratingVal = activeRating ? activeRating.value : 5;
            const categorySelect = document.getElementById('categorySelect');
            const catVal = categorySelect ? categorySelect.value : 'General';

            livePreviewBtn.disabled = true;
            livePreviewBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Running NLP Pipeline...';

            try {
                const response = await fetch('/api/analyze-live', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        text: text,
                        rating: ratingVal,
                        category: catVal
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    previewContainer.classList.remove('d-none');
                    
                    const sentEl = document.getElementById('prevSentiment');
                    sentEl.textContent = data.sentiment.toUpperCase();
                    sentEl.className = 'fw-bold ' + (data.sentiment === 'positive' ? 'text-success' : (data.sentiment === 'negative' ? 'text-danger' : 'text-secondary'));

                    document.getElementById('prevEmotion').textContent = data.emotion.toUpperCase();
                    
                    const prioEl = document.getElementById('prevPriority');
                    prioEl.textContent = data.priority.toUpperCase();
                    prioEl.className = 'fw-bold ' + (data.priority === 'critical' ? 'text-danger' : (data.priority === 'high' ? 'text-warning' : 'text-primary'));

                    document.getElementById('prevCategory').textContent = data.category;
                    document.getElementById('prevLanguage').textContent = data.language;
                    document.getElementById('prevSummary').textContent = data.summary;
                    document.getElementById('prevRecommendation').textContent = data.recommendation;
                    
                    // Smooth scroll to preview
                    previewContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            } catch (err) {
                console.error('InsightAI: Live preview error:', err);
            } finally {
                livePreviewBtn.disabled = false;
                livePreviewBtn.innerHTML = '<i class="bi bi-cpu me-1"></i> Preview AI Analysis';
            }
        });
    }
});

// Open Modern Feedback Inspection Drawer / Modal
window.openFeedbackModal = async function(feedbackId) {
    const modalEl = document.getElementById('feedbackDetailModal');
    if (!modalEl) return;
    
    const bsModal = new bootstrap.Modal(modalEl);
    bsModal.show();

    const bodyEl = document.getElementById('feedbackModalBody');
    bodyEl.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
            <p class="mt-3 text-muted small fw-semibold">Loading real-time AI intelligence...</p>
        </div>
    `;

    try {
        const response = await fetch(`/admin/feedbacks/${feedbackId}?format=json`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (response.ok) {
            const data = await response.json();
            const f = data.feedback;
            
            let sentimentBadge = f.sentiment === 'positive' ? 'badge-positive' : (f.sentiment === 'negative' ? 'badge-negative' : 'badge-neutral');
            let priorityBadge = 'badge-' + (f.priority || 'low');
            let sentimentScore = parseFloat(f.sentiment_score || 0);
            let scoreText = (sentimentScore !== 0) ? `Polarity Score: ${sentimentScore > 0 ? '+' : ''}${sentimentScore.toFixed(2)}` : 'Polarity Score: 0.00';

            bodyEl.innerHTML = `
                <div class="row g-4">
                    <!-- Customer Context -->
                    <div class="col-md-6">
                        <span class="text-muted small fw-semibold d-block mb-1">Customer Profile</span>
                        <div class="d-flex align-items-center gap-2">
                            <div class="avatar-initials">${(f.customer_name || 'U').substring(0, 1).toUpperCase()}</div>
                            <div>
                                <div class="fw-bold text-dark">${f.customer_name}</div>
                                <div class="text-muted small">${f.customer_email}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <span class="text-muted small fw-semibold d-block mb-1">Given Rating</span>
                        <div class="star-display">★ ${f.rating} / 5.0</div>
                    </div>
                    <div class="col-md-3">
                        <span class="text-muted small fw-semibold d-block mb-1">Detected Language</span>
                        <span class="badge bg-light text-dark border">${f.language}</span>
                    </div>

                    <!-- Original Raw Feedback -->
                    <div class="col-12">
                        <span class="text-muted small fw-semibold d-block mb-1">Customer Voice (Raw Feedback)</span>
                        <div class="p-3 bg-light rounded-3 border text-dark" style="font-size: 0.95rem; line-height: 1.6;">
                            "${f.feedback_text}"
                        </div>
                    </div>

                    <!-- Visual AI Analysis Section -->
                    <div class="col-12">
                        <div class="card p-3 bg-light border-0">
                            <span class="text-uppercase fw-bold text-primary small mb-3 d-flex align-items-center gap-2">
                                <i class="bi bi-cpu-fill"></i> AI Pipeline Telemetry
                            </span>
                            <div class="row g-3">
                                <div class="col-sm-6 col-md-3">
                                    <span class="text-muted small d-block">Sentiment</span>
                                    <span class="${sentimentBadge} mt-1">${f.sentiment.toUpperCase()}</span>
                                    <div class="small text-muted mt-1">${scoreText}</div>
                                </div>
                                <div class="col-sm-6 col-md-3">
                                    <span class="text-muted small d-block">Detected Emotion</span>
                                    <div class="fw-bold text-dark mt-1">${f.emotion ? f.emotion.toUpperCase() : 'NEUTRAL'}</div>
                                </div>
                                <div class="col-sm-6 col-md-3">
                                    <span class="text-muted small d-block">Category</span>
                                    <span class="badge bg-white text-dark border mt-1">${f.category}</span>
                                </div>
                                <div class="col-sm-6 col-md-3">
                                    <span class="text-muted small d-block">Priority Level</span>
                                    <span class="${priorityBadge} mt-1">${f.priority.toUpperCase()}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- AI Summary -->
                    <div class="col-12">
                        <div class="p-3 bg-white rounded-3 border border-start border-3 border-primary">
                            <span class="text-muted small fw-semibold d-block mb-1">
                                <i class="bi bi-file-text me-1 text-primary"></i> AI Executive Summary
                            </span>
                            <p class="mb-0 text-dark small fw-medium">${f.summary || 'Summary unavailable.'}</p>
                        </div>
                    </div>

                    <!-- Business Recommendation -->
                    <div class="col-12">
                        <div class="p-3 bg-white rounded-3 border border-start border-3 border-success">
                            <span class="text-muted small fw-semibold d-block mb-1">
                                <i class="bi bi-lightbulb-fill me-1 text-success"></i> Actionable Recommendation
                            </span>
                            <p class="mb-0 text-dark small fw-medium">${f.recommendation || 'Recommendation unavailable.'}</p>
                        </div>
                    </div>
                </div>
            `;
            
            // Wire update form
            const formAction = document.getElementById('feedbackUpdateForm');
            if (formAction) {
                formAction.action = `/admin/feedbacks/${f.id}/update`;
                const stSelect = document.getElementById('modalStatusSelect');
                if (stSelect) stSelect.value = f.status;
                const prSelect = document.getElementById('modalPrioritySelect');
                if (prSelect) prSelect.value = f.priority;
                const ntInput = document.getElementById('modalAdminNotes');
                if (ntInput) ntInput.value = f.admin_notes || '';
            }
        }
    } catch (e) {
        bodyEl.innerHTML = '<div class="alert alert-danger">Error retrieving feedback intelligence.</div>';
    }
};
