from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True, nullable=False)
    file_type = Column(String)  # pdf or txt
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer)
    metadata_json = Column(Text)  # page number, etc.
    vector_id = Column(String, unique=True)  # Pinecone vector ID
    document = relationship("Document", back_populates="chunks")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    date = Column(String, nullable=False)  # or Date if you prefer
    time = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)