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
    user_id: str,
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
                "user_id": user_id,
                "memory_type": memory_type,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        ]
    )


def get_user_memories(
    user_id: str,
    status: str | None = None
) -> list[dict]:

    if status:
        where = {
            "$and": [
                {"user_id": user_id},
                {"status": status}
            ]
        }
    else:
        where = {
            "user_id": user_id
        }

    results = collection.get(where=where)

    memories = []

    ids = results.get("ids", [])
    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    for memory_id, document, metadata in zip(
        ids,
        documents,
        metadatas
    ):
        memories.append({
            "id": memory_id,
            "text": document,
            "metadata": metadata
        })

    return memories

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


def store_user_preference(text: str, user_id: str) -> None:
    store_memory(
        text=text,
        user_id=user_id,
        role="user",
        memory_type="preference",
        status="active"
    )


def get_user_preferences(user_id: str) -> list[str]:
    results = collection.get(
        where={
            "$and": [
                {"user_id": user_id},
                {"memory_type": "preference"},
                {"status": "active"}
            ]
        }
    )
    return results.get("documents", [])


def store_user_memory(text: str, user_id: str) -> None:
    store_memory(
        text=text,
        user_id=user_id,
        role="user",
        memory_type="user_memory",
        status="active"
    )


def retrieve_user_memories(
    query: str,
    user_id: str,
    n_results: int = 3,
    query_embedding: list[float] | None = None,
    include_distances: bool = False
) -> list:
    if query_embedding is None:
        query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={
            "$and": [
                {"user_id": user_id},
                {"memory_type": "user_memory"},
                {"status": "active"}
            ]
        }
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if include_distances:
        return [
            {
                "text": document,
                "distance": round(distance, 4)
            }
            for document, distance in zip(documents, distances)
        ]

    return documents

def store_chat_summary(
    text: str,
    session_id: str,
    user_id: str,
    existing_id: str | None = None
) -> str:
    embedding = create_embedding(text)

    metadata = {
        "role": "system",
        "user_id": user_id,
        "memory_type": "chat_summary",
        "status": "active",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat()
    }

    if existing_id:
        collection.update(
            ids=[existing_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata]
        )
        return existing_id

    memory_id = str(uuid.uuid4())

    collection.add(
        ids=[memory_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata]
    )

    return memory_id


def retrieve_chat_summaries(
    query: str,
    user_id: str,
    n_results: int = 2,
    query_embedding: list[float] | None = None,
    include_distances: bool = False
) -> list:
    if query_embedding is None:
        query_embedding = create_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={
            "$and": [
                {"user_id": user_id},
                {"memory_type": "chat_summary"},
                {"status": "active"}
            ]
        }
    )

    documents = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]

    if include_distances:
        return [
            {
                "text": document,
                "distance": round(distance, 4)
            }
            for document, distance in zip(documents, distances)
        ]

    return documents


def retrieve_context(query: str, user_id: str) -> dict:
    query_embedding = create_embedding(query)
    preferences = get_user_preferences(user_id=user_id)
    user_memories = retrieve_user_memories(
        query=query,
        user_id=user_id,
        n_results=7,
        query_embedding=query_embedding,
        include_distances=True
    )
    session_summaries = retrieve_chat_summaries(
        query=query,
        user_id=user_id,
        n_results=2,
        query_embedding=query_embedding,
        include_distances=True
    )
    return {
        "preferences": preferences,
        "user_memories": user_memories,
        "chat_summaries": session_summaries
    }


def should_store_memory(
    text: str,
    user_id: str,
    memory_type: str,
    duplicate_threshold: float = 0.45
) -> dict:
    similar_memories = find_similar_active_memories(
        query=text,
        user_id=user_id,
        memory_type=memory_type,
        n_results=1
    )

    if not similar_memories:
        return {
            "store": True,
            "reason": "no_similar_memory_found",
            "closest_memory": None,
            "distance": None,
            "threshold": duplicate_threshold
        }

    closest_memory = similar_memories[0]
    distance = closest_memory["distance"]

    if distance <= duplicate_threshold:
        return {
            "store": False,
            "reason": "duplicate_memory",
            "closest_memory": closest_memory["text"],
            "distance": distance,
            "threshold": duplicate_threshold
        }

    return {
        "store": True,
        "reason": "similar_but_above_threshold",
        "closest_memory": closest_memory["text"],
        "distance": distance,
        "threshold": duplicate_threshold
    }

def find_similar_active_memories(
    query: str,
    user_id: str,
    memory_type: str,
    n_results: int = 3
) -> list[dict]:
    query_embedding = create_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={
            "$and": [
                {"user_id": user_id},
                {"memory_type": memory_type},
                {"status": "active"}
            ]
        }
    )
    memories = []
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for memory_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances
    ):
        memories.append(
            {
                "id": memory_id,
                "text": document,
                "metadata": metadata,
                "distance": distance
            }
        )

    return memories


def mark_memory_obsolete(
    memory_id: str,
    reason: str = "manual_obsolete",
    replaced_by: str | None = None
) -> None:
    result = collection.get(
        ids=[memory_id]
    )

    documents = result.get("documents", [])
    metadatas = result.get("metadatas", [])

    if not documents or not metadatas:
        return

    metadata = metadatas[0]

    metadata["status"] = "obsolete"
    metadata["obsolete_reason"] = reason
    metadata["updated_at"] = datetime.now().isoformat()

    if replaced_by:
        metadata["replaced_by"] = replaced_by

    collection.update(
        ids=[memory_id],
        metadatas=[metadata]
    )

def restore_memory(
    memory_id: str,
    reason: str = "manual_restore"
) -> None:
    result = collection.get(ids=[memory_id])

    documents = result.get("documents", [])
    metadatas = result.get("metadatas", [])

    if not documents or not metadatas:
        return
    metadata = metadatas[0]
    metadata["status"] = "active"
    metadata["restore_reason"] = reason
    metadata["restored_at"] = datetime.now().isoformat()
    collection.update(
        ids=[memory_id],
        metadatas=[metadata]
    )