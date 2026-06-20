from core.memory_manager import (
    store_user_preference,
    store_user_memory,
    store_session_summary,
    get_user_preferences,
    retrieve_user_memories,
    retrieve_session_summaries,
)

store_user_preference("Ο χρήστης προτιμά σύντομες απαντήσεις.")
store_user_memory("Ο χρήστης λέγεται Άγγελος.")
store_user_memory("Ο χρήστης γράφει διπλωματική για μνήμη σε LLMs.")
store_session_summary(
    "Στη συνομιλία συζητήθηκε η χρήση ChromaDB και embeddings για μακροπρόθεσμη μνήμη.",
    session_id="test-session-1"
)

query = "Πώς με λένε και τι θέμα έχει η διπλωματική μου;"

print("Preferences:")
print(get_user_preferences())

print("\nUser memories:")
print(retrieve_user_memories(query, n_results=3))

print("\nSession summaries:")
print(retrieve_session_summaries(query, n_results=2))