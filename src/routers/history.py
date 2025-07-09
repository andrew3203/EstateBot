from fastapi import APIRouter, Query, Request

from src.schema.history import HistoryModel
from src.service.history import UserHistory


router = APIRouter()


@router.get("", response_model=HistoryModel)
async def get_history(
    request: Request,
    user_id: str = Query(description="user id"),
    limit: int = Query(default=10),
    offset: int = Query(default=0),
) -> HistoryModel:
    service: UserHistory = request.app.state.user_history
    return await service.get(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
