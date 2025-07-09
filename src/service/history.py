from datetime import datetime, UTC
import logging
from src.repo.history import get_user_messages_paginated
from src.shema.history import HostoryModel, ChatItem
from src.utils.singleton import SingletonMeta
from src.utils.сache import ThreadSafeLRUCache
from src.db import get_session

logger = logging.getLogger(__name__)


class UserHistory(metaclass=SingletonMeta):
    def __init__(
        self,
        cache: ThreadSafeLRUCache,
        messages_limit: int | None = None,
    ):
        self.cache = cache
        self.messages_limit = messages_limit or 10

    def _get_key(self, user_id: int, course_uuid: str | None = None) -> str:
        return f"{user_id}-{course_uuid}" if course_uuid else f"{user_id}"

    def check(slelf, model: HostoryModel):
        return model.spent <= model.limit

    def get(
        self,
        user_id: int,
        course_uuid: str | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> HostoryModel:
        key = self._get_key(user_id=user_id, course_uuid=course_uuid)

        model = self.cache.get(key=key)
        spent = 0
        if model and offset == 0:
            data = HostoryModel.model_validate(model)
            spent = data.spent
            if len(data.data) >= limit:
                return HostoryModel(
                    data=data.data[-limit:],
                    spent=data.spent,
                    limit=data.limit,
                )

        messages: list[ChatItem] = []
        try:
            for session in get_session():
                messages = get_user_messages_paginated(
                    session=session,
                    user_id=user_id,
                    course_uuid=course_uuid,
                    limit=limit,
                    offset=offset,
                )
        except Exception as e:
            logger.error(f"Error fetching data from db {user_id=}: {e}", exc_info=True)

        data = HostoryModel(data=messages, spent=spent, limit=self.messages_limit)
        if offset == 0 and messages:
            self.cache.set(key=key, value=data.model_dump())

        return data

    def update(
        self,
        user_id: int,
        course_uuid: str,
        answer: str,
        user_read_at: datetime,
        question: str,
    ) -> HostoryModel:
        model = self.get(user_id=user_id, course_uuid=course_uuid)
        model.data.append(
            ChatItem(
                user=question,
                user_read_at=user_read_at,
                assistant=answer,
                assistent_send_at=datetime.now(UTC),
            )
        )
        model.spent += 1
        key = self._get_key(user_id=user_id, course_uuid=course_uuid)
        self.cache.set(key=key, value=model.model_dump(mode="json"))
