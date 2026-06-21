import os
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-5.4-mini-2026-03-17"

def generate_response(messages: list[dict]) -> str:
    try:
        response = client.responses.create(
            model=MODEL,
            input=messages,
            max_output_tokens=1500
        )
        return response.output_text
    except RateLimitError:
        return (
            "Δεν υπάρχει διαθέσιμο OpenAI quota. "
            "Έλεγξε billing ή API credits."
        )
    except Exception as e:
        return f"Σφάλμα κατά την κλήση του μοντέλου: {e}"