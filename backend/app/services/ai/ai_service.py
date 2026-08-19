import json
import time
from typing import List, Dict

from openai import OpenAI
from app.core.config import settings
from app.services.ai.prompts import build_batch_classification_prompt

client = OpenAI(api_key=settings.OPENAI_API_KEY)

MAX_RETRIES = 3
RETRY_DELAY = 2


# ------------------------
# Core AI call
# ------------------------
def call_ai(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON."},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    print("TOKEN USAGE:", response.usage)

    return response.choices[0].message.content


# ------------------------
# Retry wrapper
# ------------------------
def call_ai_with_retry(prompt: str) -> str:
    last_exception = None

    for attempt in range(MAX_RETRIES):
        try:
            return call_ai(prompt)

        except Exception as e:
            print(f"AI call failed (attempt {attempt+1}): {e}")
            last_exception = e
            time.sleep(RETRY_DELAY * (attempt + 1))

    raise last_exception


# ------------------------
# Clean JSON safely
# ------------------------
def parse_json_response(raw_text: str):
    raw_text = raw_text.strip()

    # Remove markdown formatting
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()

    try:
        return json.loads(raw_text)

    except json.JSONDecodeError:
        print("❌ JSON PARSE ERROR")
        print("RAW AI RESPONSE:\n", raw_text)
        raise


# ------------------------
# Single batch
# ------------------------
def classify_ticket_batch(
    tickets: List[Dict],
    categories: List[Dict],
) -> List[Dict]:

    prompt = build_batch_classification_prompt(tickets, categories)

    # Debug (optional but useful)
    print(f"\n📦 Sending batch of {len(tickets)} tickets to AI...\n")

    raw_text = call_ai_with_retry(prompt)

    parsed = parse_json_response(raw_text)

    # Safety check
    if not isinstance(parsed, list):
        raise ValueError("AI response is not a list")

    return parsed


# ------------------------
# Batch runner
# ------------------------
def classify_tickets_in_batches(
    tickets: List[Dict],
    categories: List[Dict],
    batch_size: int = 25,
) -> List[Dict]:

    results = []

    for i in range(0, len(tickets), batch_size):
        batch = tickets[i : i + batch_size]

        print(f"🚀 Processing batch {i // batch_size + 1}...")

        batch_result = classify_ticket_batch(batch, categories)

        results.extend(batch_result)

    return results