import json

from core.llm_client import client

MODEL = "gpt-5.4-mini-2026-03-17"


def check_memory_conflict(
    new_memory: str,
    existing_memory: str
) -> dict:
    prompt = f"""
You check whether a new memory contradicts or replaces an existing memory.

Existing memory:
{existing_memory}

New memory:
{new_memory}

Return only valid JSON in this exact format:
{{
  "conflict": true,
  "reason": "short explanation in Greek"
}}

Rules:
- conflict is true only if the new memory clearly contradicts, replaces, or updates the existing memory.
- conflict is false if both memories can coexist.
- Return ONLY valid JSON.
- Do not use markdown.
- Do not add explanations.
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    try:
        return json.loads(response.output_text)
    except json.JSONDecodeError:
        return {
            "conflict": False,
            "reason": "Αποτυχία ανάγνωσης JSON από το μοντέλο."
        }