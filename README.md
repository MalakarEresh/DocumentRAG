# Document RAG System

A RAG implementation using Google Gemini 2.5-pro model for conversation and Huggingface embedding model for vector-embedding.

## Installation

Install my-project

```bash
  python -m venv .venv
  .\.venv\Scripts\Activate
  pip install -r requirements.txt
```

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`PINECONE_API_KEY`

`PINECONE_ENVIRONMENT`

`GOOGLE_GEMINI_API_KEY`

`REDIS_URL`

`DATABASE_URL: sqlite+aiosqlite:///./YOUR_DB_NAME.db`

`JWT_SECRET_KEY: RANDOM STRING`

## Deployment

To deploy this project run

```bash
# Run the uvicorn server
  uvicorn main:app --reload
```

```bash
# uvicorn runs on
  http://127.0.0.1:8000
```

## Tech Stack

**Server:** FastAPI, Redis, Pinecone, Gemini-2.5-pro, Huggingface, Langchain, SQLite
