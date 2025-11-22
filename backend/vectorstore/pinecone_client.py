from pinecone import Pinecone, ServerlessSpec
from config import settings


pc = Pinecone(api_key=settings.PINECONE_API_KEY)
INDEX_NAME = settings.PINECONE_INDEX_NAME

if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(INDEX_NAME)


def get_namespace(session_id: str) -> str:
    return f"session-{session_id}"


def delete_session_vectors(session_id: str):
    namespace = get_namespace(session_id)
    index.delete(namespace=namespace, delete_all=True)