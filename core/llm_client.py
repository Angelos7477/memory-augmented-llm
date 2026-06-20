import os
from openai import OpenAI
from openai import RateLimitError
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-5.4-mini-2026-03-17",
            messages=messages,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except RateLimitError:
        return "Δεν υπάρχει διαθέσιμο OpenAI quota. Έλεγξε billing ή API credits."