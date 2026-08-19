# app/test_ai.py

from app.services.ai_service import classify_tickets_in_batches
from app.repositories.category_repository import format_categories_for_ai

# mock categories (for now)
categories = [
    {
        "main_category": "Order",
        "subcategory": "Where is my order",
        "description": "Tracking inquiries",
    },
    {
        "main_category": "Account",
        "subcategory": "Update email",
        "description": "Change email requests",
    },
]

tickets = [
    {
        "customer_message": "Where is my order?",
        "agent_response": "Let me check that for you.",
    },
    {
        "customer_message": "I want to change my email",
        "agent_response": "Sure, I can help.",
    },
]

results = classify_tickets_in_batches(tickets, categories)

print(results)