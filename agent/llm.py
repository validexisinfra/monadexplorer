import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def call_llm(prompt: str) -> str:
    resp = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    return resp.text
