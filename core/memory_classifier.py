import json

from core.llm_client import client

MODEL = "gpt-5.4-mini-2026-03-17"


def classify_memory(user_input: str) -> dict:
    prompt = f"""
You classify whether the user's message should be stored as long-term memory.

User message:
{user_input}

Memory types:
- preference: how the user wants the assistant to behave or respond
- user_memory: stable information about the user, their projects, interests, goals, or personal facts
- ignore: temporary conversation, question, instruction, or information not useful later

Return only valid JSON in this exact format:
{{
  "memory_type": "preference" | "user_memory" | "ignore",
  "memory_text": "clean memory sentence or empty string"
  "reason": "short reason for the decision",
  "confidence": 0.0
}}

Rules:
- Use "preference" for response style preferences.
- Use "user_memory" for stable user facts, goals, interests, or ongoing projects.
- Use "ignore" for ordinary questions or temporary discussion.
- memory_text must be written in Greek.
- memory_text must be a complete sentence.
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
            "memory_type": "ignore",
            "memory_text": "",
            "reason": "Αποτυχία ανάγνωσης JSON από το μοντέλο.",
            "confidence": 0.0
        }