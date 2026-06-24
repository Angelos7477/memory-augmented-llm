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
    user_id: str,
    session_id: str,
    memory_enabled: bool,
    retrieval_latency_ms: float,
    llm_latency_ms: float,
    total_latency_ms: float,
    classification: dict | None = None,
    memory_storage: list[dict] | None = None
) -> None:

    now = datetime.now()

    date_folder = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%H%M%S")

    user_log_dir = (
        LOG_DIR
        / user_id
        / date_folder
    )

    user_log_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = user_log_dir / f"{timestamp}.json"

    payload = {
        "timestamp": now.isoformat(),
        "user_id": user_id,
        "session_id": session_id,
        "memory_enabled": memory_enabled,
        "retrieval_latency_ms": retrieval_latency_ms,
        "llm_latency_ms": llm_latency_ms,
        "total_latency_ms": total_latency_ms,
        "user_input": user_input,
        "retrieved_context": context,
        "current_session_summary": session_summary,
        "messages_for_llm": messages_for_llm,
        "assistant_message": {
            "role": "assistant",
            "content": assistant_response
        },
        "memory_classification": classification,
        "memory_storage": memory_storage
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