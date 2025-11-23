from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str = "rag-index"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    GOOGLE_GEMINI_API_KEY: str
    LLM_MODEL: str = "gemini-2.5-pro" 

    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "sqlite+aiosqlite:///./rag.db"
    JWT_SECRET_KEY:str

    FRONTEND_URL:str

    

    class Config:
        env_file = ".env"

settings = Settings()