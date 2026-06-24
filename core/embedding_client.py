from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MAX_EMBEDDING_CHARS = 8000

def create_embedding(text: str):
    original_length = len(text)
    text = text[:MAX_EMBEDDING_CHARS]
    if original_length > MAX_EMBEDDING_CHARS:
        print(
            f"Embedding input truncated from "
            f"{original_length} to {MAX_EMBEDDING_CHARS} chars"
        )
    print("Creating embedding for:", text[:50])
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding