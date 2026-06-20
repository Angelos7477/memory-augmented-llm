import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def log_prompt(
    user_input: str,
    context: dict,
    session_summary: str,
    messages_for_llm: list[dict],
    assistant_response: str,
    classification: dict | None = None
) -> None:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = LOG_DIR / f"prompt_{timestamp}.json"

    payload = {
    "user_input": user_input,
    "retrieved_context": context,
    "current_session_summary": session_summary,
    "messages_for_llm": messages_for_llm,
    "assistant_message": {
        "role": "assistant",
        "content": assistant_response
    },
    "memory_classification": classification
}

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            payload,
            f,
            indent=2,
            ensure_ascii=False
        )