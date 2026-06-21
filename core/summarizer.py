from core.llm_client import client

MODEL = "gpt-5.4-mini-2026-03-17"


def update_session_summary(
    current_summary: str,
    messages_to_summarize: list[dict]
) -> str:

    conversation_text = ""

    for message in messages_to_summarize:
        role = message["role"].upper()
        content = message["content"]

        conversation_text += f"{role}: {content}\n"

    prompt = f"""
You update the short-term summary of the current chat session.

Existing session summary:
{current_summary if current_summary else "None"}

New conversation segment:
{conversation_text}

Create an updated SESSION summary.

Rules:
- Summarize only what was discussed in this current chat session.
- Focus on implementation decisions, debugging findings, current task, and unresolved next steps.
- Do not include stable user profile facts such as name, preferences, or thesis topic unless they are directly relevant to the current task.
- Do not include exact dialogue, apologies, numbering games, or temporary back-and-forth.
- Maximum length: 4 bullet points.
- If the conversation segment is only casual small talk without useful context, keep the summary very short.
- Do not over-summarize greetings, casual checks, or empty social exchanges.
- If nothing important happened, write: "Δεν προέκυψε σημαντική πληροφορία στη συζήτηση."
- Write in Greek.
- Return only the updated summary.
"""

    response = client.responses.create(
        model=MODEL,
        input=prompt
    )

    return response.output_text

