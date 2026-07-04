"""Prompt templates for AI response generation."""

RESPONSE_GENERATION_SYSTEM = """You are a professional customer support agent for a SaaS company.
Your goal is to provide helpful, empathetic, and accurate responses to customer inquiries.

Guidelines:
1. Always be professional and empathetic
2. Acknowledge the customer's concern
3. Provide clear, actionable steps
4. If unsure, indicate that the issue will be escalated
5. Use the knowledge base information provided to give accurate answers
6. Include troubleshooting steps when applicable
7. Keep responses concise but thorough

Tone: Professional, friendly, solution-oriented
Format: Use clear paragraphs and bullet points for steps"""

RESPONSE_GENERATION_USER = """Generate a professional response for this support ticket:

Ticket Details:
- Subject: {subject}
- Description: {description}
- Category: {category}
- Priority: {priority}
- Customer Name: {customer_name}

Relevant Knowledge Base Articles:
{knowledge_context}

Respond in this exact JSON format:
{{
    "response": "<professional response to the customer>",
    "troubleshooting_steps": "<numbered steps if applicable, or null>",
    "confidence": <float between 0 and 1>,
    "requires_escalation": <true or false>,
    "escalation_reason": "<reason if requires_escalation is true, or null>"
}}"""

KNOWLEDGE_SEARCH_QUERY = """Based on this support ticket, generate a search query for the knowledge base:

Subject: {subject}
Description: {description}
Category: {category}

Return a concise search query (3-5 keywords) that would find relevant documentation."""
