import uuid
from datetime import datetime

import chromadb

from core.embedding_client import create_embedding


chroma_client = chromadb.PersistentClient(
    path="data/chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="chat_memory"
)


def store_memory(
    text: str,
    role: str = "user",
    memory_type: str = "conversation",
    status: str = "active"
) -> None:
    memory_id = str(uuid.uuid4())
    embedding = create_embedding(text)
    collection.add(
        ids=[memory_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[
            {
                "role": role,
                "memory_type": memory_type,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        ]
    )


#def retrieve_memories(query: str, n_results: int = 3) -> list[str]:
#    query_embedding = create_embedding(query)
#    results = collection.query(
#        query_embeddings=[query_embedding],
#        n_results=n_results,
#        where={"status": "active"}
#    )
#    documents = results.get("documents", [[]])[0]
#    return documents


def get_all_memories() -> list[dict]:
    results = collection.get()
    memories = []
    ids = results.get("ids", [])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    for memory_id, document, metadata in zip(ids, documents, metadatas):
        memories.append(
            {
                "id": memory_id,
                "text": document,
                "metadata": metadata
            }
        )
    return memories


def store_user_preference(text: str) -> None:
    store_memory(
        text=text,
        role="user",
        memory_type="preference",
        status="active"
    )


def get_user_preferences() -> list[str]:
    results = collection.get(
        where={
            "$and": [
                {"memory_type": "preference"},
                {"status": "active"}
            ]
        }
    )
    return results.get("documents", [])


def store_user_memory(text: str) -> None:
    store_memory(
        text=text,
        role="user",
        memory_type="user_memory",
        status="active"
    )


def retrieve_user_memories(
    query: str,
    n_results: int = 3,
    query_embedding: list[float] | None = None
) -> list[str]:
    if query_embedding is None:
        query_embedding = create_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={
            "$and": [
                {"memory_type": "user_memory"},
                {"status": "active"}
            ]
        }
    )
    return results.get("documents", [[]])[0]


def store_session_summary(text: str, session_id: str) -> None:
    memory_id = str(uuid.uuid4())
    embedding = create_embedding(text)

    collection.add(
        ids=[memory_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[
            {
                "role": "system",
                "memory_type": "session_summary",
                "status": "active",
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        ]
    )


def retrieve_session_summaries(
    query: str,
    n_results: int = 2,
    query_embedding: list[float] | None = None
) -> list[str]:
    if query_embedding is None:
        query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={
            "$and": [
                {"memory_type": "session_summary"},
                {"status": "active"}
            ]
        }
    )

    return results.get("documents", [[]])[0]


def retrieve_context(query: str) -> dict:
    query_embedding = create_embedding(query)
    preferences = get_user_preferences()
    user_memories = retrieve_user_memories(
        query=query,
        n_results=3,
        query_embedding=query_embedding
    )
    session_summaries = retrieve_session_summaries(
        query=query,
        n_results=2,
        query_embedding=query_embedding
    )
    return {
        "preferences": preferences,
        "user_memories": user_memories,
        "chat_summaries": session_summaries
    }