def format_list(title: str, items: list) -> str:
    if not items:
        return f"{title}:\n- None\n"

    formatted_items = []

    for item in items:
        if isinstance(item, dict):
            text = item.get("text", "")
            formatted_items.append(f"- {text}")
        else:
            formatted_items.append(f"- {item}")

    return f"{title}:\n" + "\n".join(formatted_items) + "\n"


def get_recent_history(messages: list[dict], max_messages: int = 6) -> list[dict]:
    non_system_messages = [
        message for message in messages
        if message["role"] != "system"
    ]

    return non_system_messages[-max_messages:]


def build_messages(
    user_input: str,
    context: dict,
    session_summary: str,
    conversation_messages: list[dict]
) -> list[dict]:

    preferences = context.get("preferences", [])
    user_memories = context.get("user_memories", [])
    chat_summaries = context.get("chat_summaries", [])

    recent_messages = get_recent_history(
        conversation_messages,
        max_messages=6
    )

    system_content = f"""
You are a helpful memory-augmented assistant.

Use the memory context only when relevant.
If the user asks for the current conversation summary, answer using the Current Session Summary and recent messages.
Do not mention retrieval or internal memory unless the user asks.

{format_list("User Preferences", preferences)}

{format_list("Relevant User Memories", user_memories)}

{format_list("Relevant Past Chat Summaries", chat_summaries)}

Current Session Summary:
{session_summary if session_summary else "None"}
"""

    messages = [
        {
            "role": "system",
            "content": system_content
        }
    ]

    messages.extend(recent_messages)

    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    return messages