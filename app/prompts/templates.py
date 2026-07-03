"""Prompt templates for AI/LLM integrations.

Store reusable prompt templates here for chatbot or RAG features.
"""

SYSTEM_PROMPT = """You are an HR assistant. Answer questions about company policies,
employee benefits, and HR processes based on the provided context."""

QA_PROMPT = """Context:
{context}

Question: {question}

Answer the question based only on the provided context. If the answer is not in the
context, say "I don't have information about that in the current policy documents."
"""
