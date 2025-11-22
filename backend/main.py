from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, EmailStr, validator
import uuid
import re

from config import settings
from services.ingestion import ingest_document
from services.rag import rag_query
from database.models import Base, Booking
from vectorstore.pinecone_client import index, get_namespace
from fastapi.middleware.cors import CORSMiddleware

# ====================== DATABASE ======================
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

# ====================== APP ======================
app = FastAPI(
    title="Custom RAG",
    description="Upload PDF → Chat → Book → New Chat",
    version="2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Use localhost only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====================== BOOKING MODEL ======================
class BookingRequest(BaseModel):
    name: str
    email: EmailStr
    date: str
    time: str

    @validator("date")
    def validate_date(cls, v):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be YYYY-MM-DD")
        return v

    @validator("time")
    def validate_time(cls, v):
        if not re.match(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", v):
            raise ValueError("Time must be HH:MM (24h)")
        return v

# ====================== STARTUP ======================
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ====================== ENDPOINTS ======================

@app.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    chunking_strategy: str = Form("recursive"),
    db: AsyncSession = Depends(get_db)
):
    print("="*50)
    print("[UPLOAD] Request received")
    print(f"[UPLOAD] All cookies: {dict(request.cookies)}")
    
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(400, detail="Only PDF/TXT allowed")

    # Get or create session
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        print(f"[UPLOAD] Created NEW session: {session_id}")
    else:
        print(f"[UPLOAD] Using EXISTING session: {session_id}")
    
    result = await ingest_document(file=file, strategy=chunking_strategy, session_id=session_id, db=db)

    # Create response and set cookie
    response = JSONResponse({
        "status": "success",
        "chunks": result["chunks"],
        "message": "PDF uploaded successfully!",
        "session_id": session_id  # Send back for debugging
    })
    
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=False,  # Allow JS to read
        max_age=86400,
        samesite="lax",
        secure=False,
        path="/",
        domain=None  # Don't set domain, let browser handle it
    )
    
    print(f"[UPLOAD] Response: Setting cookie session_id={session_id}")
    print("="*50)
    return response


@app.post("/chat")
async def chat(
    request: Request,
    message: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    print("="*50)
    print("[CHAT] Request received")
    print(f"[CHAT] All cookies: {dict(request.cookies)}")
    
    if not message.strip():
        raise HTTPException(400, detail="Message required")

    # Get or create session
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        print(f"[CHAT] Created NEW session: {session_id}")
    else:
        print(f"[CHAT] Using EXISTING session: {session_id}")
    
    bot_response = await rag_query(session_id, message.strip())
    
    # Create response and set cookie
    response = JSONResponse({
        "response": bot_response,
        "session_id": session_id  # Send back for debugging
    })
    
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=False,
        max_age=86400,
        samesite="lax",
        secure=False,
        path="/",
        domain=None
    )
    
    print(f"[CHAT] Response: Setting cookie session_id={session_id}")
    print("="*50)
    return response


@app.post("/book-interview")
async def book_interview(
    request: Request,
    booking: BookingRequest,
    db: AsyncSession = Depends(get_db)
):
    print("="*50)
    print("[BOOKING] Request received")
    print(f"[BOOKING] All cookies: {dict(request.cookies)}")
    
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        print(f"[BOOKING] Created NEW session: {session_id}")
    else:
        print(f"[BOOKING] Using EXISTING session: {session_id}")
    
    new_booking = Booking(
        name=booking.name,
        email=booking.email,
        date=booking.date,
        time=booking.time
    )
    db.add(new_booking)
    await db.commit()

    response = JSONResponse({
        "status": "success",
        "message": f"Interview booked for {booking.name} on {booking.date} at {booking.time}!",
        "session_id": session_id
    })
    
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=False,
        max_age=86400,
        samesite="lax",
        secure=False,
        path="/"
    )
    
    print(f"[BOOKING] Response: Setting cookie session_id={session_id}")
    print("="*50)
    return response


@app.post("/new-chat")
async def new_chat(request: Request):
    print("="*50)
    print("[NEW-CHAT] Request received")
    print(f"[NEW-CHAT] All cookies: {dict(request.cookies)}")
    
    session_id = request.cookies.get("session_id")
    
    if not session_id:
        print("[NEW-CHAT] No session found")
        return JSONResponse({"message": "No active session"})

    print(f"[NEW-CHAT] Clearing session: {session_id}")
    namespace = get_namespace(session_id)

    try:
        index.delete(namespace=namespace, delete_all=True)
        print(f"[NEW-CHAT] Cleared Pinecone namespace: {namespace}")
    except Exception as e:
        print(f"[NEW-CHAT] Pinecone cleanup failed: {e}")

    # Generate new session ID
    new_session_id = str(uuid.uuid4())
    print(f"[NEW-CHAT] New session ID: {new_session_id}")
    
    response = JSONResponse({
        "message": "New chat started! Previous document removed.",
        "status": "ready_for_new_document",
        "session_id": new_session_id
    })
    
    response.set_cookie(
        key="session_id",
        value=new_session_id,
        httponly=False,
        max_age=86400,
        samesite="lax",
        secure=False,
        path="/",
        domain=None
    )
    
    print(f"[NEW-CHAT] Response: Setting cookie session_id={new_session_id}")
    print("="*50)
    return response


@app.get("/")
async def root():
    return {"message": "RAG API is running! Visit /docs"}