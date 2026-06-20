
#test_show_memories.py
from core.memory_manager import get_all_memories

memories = get_all_memories()

print(f"Total memories: {len(memories)}")
print()

for memory in memories:
    print("ID:", memory["id"])
    print("Text:", memory["text"])
    print("Metadata:", memory["metadata"])
    print("-" * 50)