from core.prompt_builder import build_messages

context = {
    "preferences": [
        "Ο χρήστης προτιμά σύντομες απαντήσεις."
    ],
    "user_memories": [
        "Ο χρήστης λέγεται Άγγελος.",
        "Ο χρήστης γράφει διπλωματική για μνήμη σε LLMs."
    ]
}

session_summary = (
    "Ο χρήστης υλοποιεί ένα memory-augmented chatbot "
    "με OpenAI API, embeddings και ChromaDB."
)

conversation_messages = [
    {"role": "system", "content": "Old system prompt."},

    {"role": "user", "content": "Μήνυμα 1"},
    {"role": "assistant", "content": "Απάντηση 1"},

    {"role": "user", "content": "Μήνυμα 2"},
    {"role": "assistant", "content": "Απάντηση 2"},

    {"role": "user", "content": "Μήνυμα 3"},
    {"role": "assistant", "content": "Απάντηση 3"},

    {"role": "user", "content": "Μήνυμα 4"},
    {"role": "assistant", "content": "Απάντηση 4"},
]

messages = build_messages(
    user_input="Πώς συνεχίζουμε την υλοποίηση;",
    context=context,
    session_summary=session_summary,
    conversation_messages=conversation_messages
)

for index, message in enumerate(messages):
    print("=" * 50)
    print("INDEX:", index)
    print("ROLE:", message["role"])
    print("CONTENT:")
    print(message["content"])