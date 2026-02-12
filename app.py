"""
app.py

Main FastAPI Application
Enterprise RAG Backend with JWT + Analytics + Streaming
"""

# =====================================================
# IMPORTS
# =====================================================

from fastapi import (
    FastAPI,
    Depends,
    Request,
    HTTPException,
    WebSocket,
    WebSocketDisconnect
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

import os

# Rate Limiting
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Token tracking
from langchain_community.callbacks import get_openai_callback

# Internal imports
from rag.qa_chain import get_chain
from auth.auth_router import router as auth_router
from auth.dependencies import get_current_user
from database import SessionLocal
from models import ChatHistory, TokenAnalytics
from analytics.analytics_router import router as analytics_router


# =====================================================
# LOGGING
# =====================================================

os.makedirs("logs", exist_ok=True)

logger.add(
    "logs/app.log",
    rotation="10 MB",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

logger.info("🚀 Application Starting...")


# =====================================================
# FASTAPI INIT
# =====================================================

app = FastAPI(
    title="AI RAG Chatbot Backend",
    version="2.3.0"
)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# RATE LIMITING
# =====================================================

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc):
    logger.warning(f"⚠ Rate limit exceeded for IP: {request.client.host}")
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please slow down."}
    )


# =====================================================
# ROUTERS
# =====================================================

app.include_router(auth_router)
app.include_router(analytics_router)


# =====================================================
# DATABASE DEPENDENCY
# =====================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# SAFE USER EXTRACTION (FIXED)
# =====================================================

def extract_user_info(current_user):
    """
    Handles BOTH:
    - Dict from JWT payload
    - SQLAlchemy User object
    """

    # If dependency returns JWT dict
    if isinstance(current_user, dict):

        # ✅ Correct mapping
        user_id = current_user.get("user_id")  # INTEGER
        user_email = current_user.get("sub")   # EMAIL

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return user_id, user_email

    # If dependency returns SQLAlchemy model
    return current_user.id, current_user.email


# =====================================================
# REQUEST SCHEMA
# =====================================================

class ChatRequest(BaseModel):
    message: str
    session_id: str
    memory_type: str = "buffer"


# =====================================================
# CHAT ENDPOINT
# =====================================================

@limiter.limit("10/minute")
@app.post("/chat")
async def chat(
    request: Request,
    body: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # ✅ Proper extraction
    user_id, user_email = extract_user_info(current_user)

    logger.info(f"💬 Chat called by user: {user_email}")

    try:
        chain = get_chain(
            session_id=body.session_id,
            memory_type=body.memory_type
        )

        with get_openai_callback() as cb:

            result = chain.invoke({
                "query": body.message
            })

            reply = result.get("result", "")

            prompt_tokens = cb.prompt_tokens
            completion_tokens = cb.completion_tokens
            total_tokens = cb.total_tokens
            total_cost = cb.total_cost

        logger.info(
            f"📊 Tokens | Prompt: {prompt_tokens} | "
            f"Completion: {completion_tokens} | "
            f"Total: {total_tokens} | Cost: ${total_cost}"
        )

        # =====================================================
        # SAVE CHAT HISTORY (FIXED - INTEGER USER ID)
        # =====================================================

        db.add(ChatHistory(
            user_id=user_id,   # ✅ INTEGER
            session_id=body.session_id,
            role="user",
            message=body.message
        ))

        db.add(ChatHistory(
            user_id=user_id,   # ✅ INTEGER
            session_id=body.session_id,
            role="bot",
            message=reply
        ))

        # =====================================================
        # SAVE TOKEN ANALYTICS (FIXED)
        # =====================================================

        db.add(TokenAnalytics(
            user_id=user_id,   # ✅ INTEGER
            session_id=body.session_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            total_cost=total_cost
        ))

        db.commit()

        logger.info("✅ Chat transaction committed")

        return {
            "user": user_email,
            "session_id": body.session_id,
            "reply": reply,
            "tokens": {
                "prompt": prompt_tokens,
                "completion": completion_tokens,
                "total": total_tokens,
                "cost": total_cost
            },
            "sources": [
                doc.metadata
                for doc in result.get("source_documents", [])
            ]
        }

    except Exception:
        logger.exception("❌ Error in chat endpoint")
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


# =====================================================
# WEBSOCKET STREAMING
# =====================================================

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):

    await websocket.accept()
    logger.info("🔌 WebSocket connection accepted")

    try:
        while True:
            data = await websocket.receive_json()

            message = data.get("message")
            session_id = data.get("session_id")
            memory_type = data.get("memory_type", "buffer")

            logger.info(f"💬 Streaming session: {session_id}")

            chain = get_chain(
                session_id=session_id,
                memory_type=memory_type
            )

            async for chunk in chain.astream({
                "query": message
            }):

                if isinstance(chunk, dict) and "result" in chunk:
                    await websocket.send_text(chunk["result"])

            await websocket.send_text("[END]")

    except WebSocketDisconnect:
        logger.warning("⚠ WebSocket disconnected")

    except Exception:
        logger.exception("❌ WebSocket error")
        await websocket.close()


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/")
def health():
    logger.info("Health endpoint checked")
    return {
        "status": "running",
        "version": "2.3.0"
    }
