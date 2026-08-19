def build_batch_classification_prompt(
    tickets: list[dict],
    categories: list[dict],
) -> str:

    categories_text = "\n".join(
        [
            f"- {c['main_category']} > {c['subcategory']}: {c.get('description') or ''}"
            for c in categories
        ]
    )

    tickets_text = "\n\n".join(
        [
            f"""TICKET {i+1}:
CUSTOMER MESSAGE:
{t['customer_message']}

AGENT RESPONSE:
{t['agent_response']}
"""
            for i, t in enumerate(tickets)
        ]
    )

    return f"""
You are an expert customer support analyst.

Your task is to classify customer support tickets accurately using ONLY the provided categories.

---------------------
CATEGORIES:
{categories_text}
---------------------

STRICT RULES:
1. Use ONLY the provided categories if there is a CLEAR match.
2. Do NOT guess or loosely match categories.
3. If no strong match exists:
   - Set main_category = null
   - Set subcategory = null
   - Suggest a new category
4. Classify as NON-SUPPORT ONLY if:
   - Duplicate
   - Marketing Emails
   - Paypal Notification
   - Billing Notifications
   - Outbound Email
   - Phone Ticket
   - System-generated messages
5. Only analyze:
   - FIRST customer message
   - FIRST HUMAN agent response
6. Ignore AI-generated responses.
7. Be consistent and deterministic.
8. Output MUST be valid JSON (no markdown, no explanation).

---------------------
OUTPUT FORMAT:
[
  {{
    "ticket_index": 1,
    "is_support_ticket": true,
    "main_category": "string or null",
    "subcategory": "string or null",
    "confidence": 0-100,
    "reason": "short explanation",
    "suggested_new_main_category": null,
    "suggested_new_subcategory": null
  }}
]
---------------------

TICKETS:
{tickets_text}
"""