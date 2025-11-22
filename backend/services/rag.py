from openai import OpenAI
from vectorstore.pinecone_client import index, get_namespace
from langchain_huggingface import HuggingFaceEmbeddings
from utils.redis_memory import get_chat_history, add_to_history
from config import settings

client = OpenAI(
    api_key=settings.GOOGLE_GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

async def rag_query(session_id: str, user_message: str):
    namespace = get_namespace(session_id)
    history = await get_chat_history(session_id)
    query_embedding = embeddings.embed_query(user_message)

    results = index.query(
        vector=query_embedding,
        top_k=6,
        include_metadata=True,
        namespace=namespace
    )

   
    if results.matches:
        context = "\n\n".join([
            f"Source: {m['metadata'].get('source', 'Document')}, Chunk {m['metadata'].get('chunk_index', '?')}\n"
            f"Content: {m['metadata'].get('text', '')}"
            for m in results.matches
        ])
    else:
        context = "No exact match found in the document, but a document has been uploaded."

    messages = [
        {"role": "system", "content": f"""You are a helpful assistant. 
A document has been uploaded by the user. Use the provided context to answer questions.

If the context is empty or irrelevant, say you couldn't find the exact info but a document is present.

Context:\n{context}"""}
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gemini-2.5-pro",
        messages=messages,
        temperature=0.3
    )

    bot_response = response.choices[0].message.content.strip()

    await add_to_history(session_id, "user", user_message)
    await add_to_history(session_id, "assistant", bot_response)

    return bot_response