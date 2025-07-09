from fastapi import APIRouter, Query, Request

from src.application.chat import ChatUseCase
from src.repo.history_queue import MessageHistoryQueue
from src.schema.ai_query import AIResponse, AIRequest
from src.service.history import UserHistory


router = APIRouter()


@router.post("", response_model=AIResponse)
async def get_answer(
    request: Request,
    data: AIRequest = Query(),
):
    chat: ChatUseCase = request.app.state.chat
    user_history: UserHistory = request.app.state.user_history
    messages_queue: MessageHistoryQueue = request.app.state.messages_queue
    return await chat.retive_ansver(
        data=data,
        user_history=user_history,
        messages_queue=messages_queue,
    )
