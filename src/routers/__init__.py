from fastapi import APIRouter
from .chat import router as _chat_router
from .history import router as _history_router


router = APIRouter()
router.include_router(_chat_router, prefix="/chat", tags=["Chat"])
router.include_router(_history_router, prefix="/history", tags=["History"])
