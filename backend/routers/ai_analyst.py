"""
Indonesia Economic Intelligence — AI Analyst Router
"""
from fastapi import APIRouter, HTTPException
from backend.models import ChatRequest, ChatResponse
from backend.services import ai_service

router = APIRouter()


@router.post("/ai/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if len(request.message) > 2000:
        raise HTTPException(status_code=400, detail="Message too long (max 2000 characters)")

    result = await ai_service.chat(
        message=request.message,
        history=[h.dict() for h in (request.history or [])],
    )
    return ChatResponse(**result)
