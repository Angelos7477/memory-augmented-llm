import json

from core.llm_client import client

MODEL = "gpt-5.4-mini-2026-03-17"


def classify_memory(user_input: str) -> dict:
    prompt = f"""
You classify whether the user's message contains information that should be stored as long-term memory.

User message:
{user_input}

Memory types:
- preference: how the user wants the assistant to behave or respond
- user_memory: stable information about the user, their projects, interests, goals, or personal facts

Return only valid JSON in this exact format:
{{
  "memories": [
    {{
      "memory_type": "preference" | "user_memory" | "ignore",
      "memory_text": "clean memory sentence or empty string",
      "reason": "short reason for the decision",
      "confidence": 0.0
    }}
  ]
}}

Rules:
- Every decision must be returned as a memory object.
- If nothing should be stored, return one object with:
  {{
  "memory_type": "ignore",
  "memory_text": "",
  "reason": "...",
  "confidence": 0.95
  }}
- A single user message may contain multiple memories.
- Split different memory types into separate memory objects.
- Use "preference" for response style preferences.
- Use "user_memory" for stable user facts, goals, interests, or ongoing projects.
- Ignore ordinary questions or temporary discussion.
- memory_text must be written in Greek.
- memory_text must be a complete sentence.
- reason must be written in Greek.
- confidence must be a number between 0 and 1.
- Return ONLY valid JSON.
- Do not use markdown.
- Do not add explanations.
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    try:
        result = json.loads(response.output_text)

        if "memories" not in result or not isinstance(result["memories"], list):
            return {"memories": []}

        return result

    except json.JSONDecodeError:
        return {
            "memories": []
        }