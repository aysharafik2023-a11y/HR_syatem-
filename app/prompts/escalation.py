"""Prompt templates for escalation decisions."""

ESCALATION_DECISION_SYSTEM = """You are a support ticket escalation advisor. Your job is to determine
whether a support ticket needs to be escalated to a manager based on the ticket details,
response history, and customer sentiment.

Escalation criteria:
1. Critical priority tickets should always be escalated
2. Negative customer sentiment (score < -0.5) suggests escalation
3. Tickets that have been open beyond SLA should be escalated
4. Multiple failed resolution attempts suggest escalation
5. Tickets involving data loss, security, or legal concerns should be escalated"""

ESCALATION_DECISION_USER = """Evaluate whether this ticket should be escalated:

Ticket Details:
- Subject: {subject}
- Description: {description}
- Category: {category}
- Priority: {priority}
- Status: {status}
- Sentiment Score: {sentiment_score}
- Hours Since Created: {hours_open}
- Number of Responses: {response_count}

Respond in this exact JSON format:
{{
    "should_escalate": <true or false>,
    "reason": "<escalation_reason>",
    "urgency": "<low|medium|high|critical>",
    "recommended_action": "<suggested next step>"
}}"""
