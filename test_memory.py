#test_memory.py
from core.memory_manager import retrieve_context

context = retrieve_context("Πώς με λένε και τι θέμα έχει η διπλωματική μου και τι είδους απαντήσεις προτιμώ;")

print("Preferences:")
for item in context["preferences"]:
    print("-", item)

print("\nUser memories:")
for item in context["user_memories"]:
    print("-", item)

print("\nSession summaries:")
for item in context["session_summaries"]:
    print("-", item)