from core.memory_classifier import classify_memory

examples = [
    "Θέλω σύντομες απαντήσεις.",
    "Με λένε Άγγελο.",
    "Γράφω διπλωματική για μνήμη σε LLMs.",
    "Τι είναι το ChromaDB;",
    "Μπορείς να μου εξηγήσεις αυτό το error;"
]

for example in examples:
    print("=" * 50)
    print(example)
    print(classify_memory(example))