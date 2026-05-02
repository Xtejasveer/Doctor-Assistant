
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent import run_agent
import asyncio
from database import SessionLocal, PromptHistory
from datetime import datetime

app = FastAPI()

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Key = session_id, Value = list of messages
conversation_store = {}


# --- Request/Response models ---
class ChatRequest(BaseModel):
    session_id: str
    message: str
    role: str = "patient"  

class ChatResponse(BaseModel):
    response: str
    session_id: str


# --- Patient chat endpoint ---
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Get or create conversation history for this session
    if request.session_id not in conversation_store:
        conversation_store[request.session_id] = []
    
    history = conversation_store[request.session_id]
    
    # Run the agent
    response = await run_agent(request.message, history, role = "patient")

    db = SessionLocal()
    db.add(PromptHistory(
        session_id=request.session_id,
        role=request.role,
        user_message=request.message,
        agent_response=response,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    db.commit()
    db.close()
    
    return ChatResponse(
        response=response,
        session_id=request.session_id
    )


# --- Doctor report endpoint ---
@app.post("/doctor/report", response_model=ChatResponse)
async def doctor_report(request: ChatRequest):
    # Get or create conversation history for this session
    if request.session_id not in conversation_store:
        conversation_store[request.session_id] = []
    
    history = conversation_store[request.session_id]
    
    # Run the agent with doctor context
    response = await run_agent(request.message, history, role = "doctor")

    db = SessionLocal()
    db.add(PromptHistory(
        session_id=request.session_id,
        role=request.role,
        user_message=request.message,
        agent_response=response,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    db.commit()
    db.close()
    
    return ChatResponse(
        response=response,
        session_id=request.session_id
    )
@app.get("/history/{session_id}")
async def get_history(session_id: str):
    db = SessionLocal()
    history = db.query(PromptHistory).filter(
        PromptHistory.session_id == session_id
    ).all()
    db.close()
    
    return {
        "session_id": session_id,
        "history": [
            {
                "id": h.id,
                "role": h.role,
                "user_message": h.user_message,
                "agent_response": h.agent_response,
                "timestamp": h.timestamp
            }
            for h in history
        ]
    }


# --- Clear conversation history ---
@app.delete("/chat/{session_id}")
async def clear_chat(session_id: str):
    if session_id in conversation_store:
        del conversation_store[session_id]
    return {"message": "Conversation cleared"}


# --- Health check ---
@app.get("/health")
async def health():
    return {"status": "ok"}