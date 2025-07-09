from datetime import datetime, UTC
import logging
from src.repo.history import get_user_messages_paginated
from src.schema.history import HistoryModel, ChatItem
from src.utils.singleton import SingletonMeta
from src.utils.cache import SafeLRUCache
from src.db import get_session

logger = logging.getLogger(__name__)


class UserHistory(metaclass=SingletonMeta):
    def __init__(
        self,
        cache: SafeLRUCache,
    ):
        self.cache = cache

    def _get_key(self, user_id: str) -> str:
        return f"{user_id}"

    async def get(
        self,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> HistoryModel:
        key = self._get_key(user_id=user_id)

        model = await self.cache.get(key=key)
        if model and offset == 0:
            data = HistoryModel.model_validate(model)
            if len(data.data) >= limit or limit == 10:
                return HistoryModel(
                    data=data.data[-limit:],
                )

        logger.info("DATA FROM DB")
        messages: list[ChatItem] = []
        try:
            async for session in get_session():
                messages = await get_user_messages_paginated(
                    session=session,
                    user_id=user_id,
                    limit=limit,
                    offset=offset,
                )
        except Exception as e:
            logger.error(f"Error fetching data from db {user_id=}: {e}", exc_info=True)

        data = HistoryModel(data=messages)
        if offset == 0 and messages:
            await self.cache.set(key=key, value=data.model_dump())

        return data

    async def update(
        self,
        user_id: str,
        answer: str,
        question: str,
    ) -> HistoryModel:
        model = await self.get(user_id=user_id)
        model.data.append(
            ChatItem(
                user=question,
                assistant=answer,
                assistant_send_at=datetime.now(UTC),
            )
        )
        key = self._get_key(user_id=user_id)
        logger.info("SET NEW")
        await self.cache.set(key=key, value=model.model_dump(mode="json"))
