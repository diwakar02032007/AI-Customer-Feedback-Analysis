def generate_recommendation(category='General', sentiment='neutral', priority='low', aspect='General'):
    """
    Generate contextual, actionable business recommendations for managers and operational teams.
    """
    cat = (category or 'General').strip()
    sent = (sentiment or 'neutral').strip().lower()
    prio = (priority or 'low').strip().lower()

    if prio == 'critical':
        if 'Billing' in cat or aspect == 'Pricing':
            return "Escalate immediately to finance team, audit payment gateway transaction logs, and initiate proactive customer call within 1 hour."
        elif 'Quality' in cat or aspect == 'Product Quality':
            return "Trigger urgent RMA/replacement protocol, issue return shipping label, and alert quality assurance manager."
        else:
            return "Immediate tier-3 manager outreach required within 2 hours to prevent customer churn and negative brand exposure."

    if prio == 'high':
        if 'Support' in cat:
            return "Reassign ticket to a senior customer success manager and review first-contact resolution SLA."
        elif 'Usability' in cat or aspect == 'Features/Performance':
            return "Log an urgent defect ticket for frontend/backend engineering to reproduce and fix latency or crashes."
        elif 'Delivery' in cat:
            return "Contact logistics courier partner for package status verification and issue delivery credit voucher."
        else:
            return "Schedule priority follow-up with customer support lead within 6 hours."

    if sent == 'negative':
        return f"Audit operational workflow for {cat}. Gather customer contact details to offer resolution."

    if sent == 'positive':
        if 'Support' in cat:
            return "Commend the assigned customer support representative during weekly team review and record CSAT success."
        elif 'Usability' in cat or aspect == 'UI/UX':
            return "Document successful design patterns and feature implementations for cross-team knowledge sharing."
        else:
            return "Request customer permission to feature this feedback as a public testimonial or case study."

    # Neutral
    return f"Monitor {cat} metrics and incorporate suggestions into next sprint roadmap review."
