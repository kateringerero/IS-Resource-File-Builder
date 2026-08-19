from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()  # 👈 THIS LINE IS IMPORTANT

api_key = os.getenv("OPENAI_API_KEY")

print("API KEY:", api_key)  # debug

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=[
        {"role": "user", "content": "Return JSON: {\"message\": \"hello\"}"}
    ],
    temperature=0,
)

print(response.choices[0].message.content)