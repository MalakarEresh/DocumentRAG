from pydantic import BaseModel, EmailStr
from typing import Literal

class UploadRequest(BaseModel):
    chunking_strategy: Literal["recursive", "semantic", "token"] = "recursive"

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    message: str

class BookingRequest(BaseModel):
    name: str
    email: EmailStr
    date: str       
    time: str       
    session_id: str  