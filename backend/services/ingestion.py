from fastapi import UploadFile
from PyPDF2 import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession
from vectorstore.pinecone_client import index, get_namespace
from chunking.strategies import get_chunks
from langchain_huggingface import HuggingFaceEmbeddings
import uuid

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

async def ingest_document(file: UploadFile, strategy: str, session_id: str, db: AsyncSession):
    content = ""
    filename = file.filename

    if filename.endswith(".pdf"):
        reader = PdfReader(file.file)
        content = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        content = (await file.read()).decode()

    chunks = get_chunks(content, strategy)
    namespace = get_namespace(session_id)

    vectors_to_upsert = []
    for i, chunk_text in enumerate(chunks):
        vector_id = str(uuid.uuid4())
        embedding = embeddings.embed_query(chunk_text)

        vectors_to_upsert.append({
            "id": vector_id,
            "values": embedding,
            "metadata": {
                "text": chunk_text[:500],
                "source": filename,
                "chunk_index": i
            }
        })

    # Upload only to this user's namespace
    index.upsert(vectors=vectors_to_upsert, namespace=namespace)

    return {"chunks": len(chunks)}