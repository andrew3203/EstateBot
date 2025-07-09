from sqlmodel import Session, select
from sqlmodel import desc
from src.models.history import MessageHistory
from src.schema.history import ChatItem


async def get_user_messages_paginated(
    session: Session,
    user_id: int,
    limit: int = 10,
    offset: int = 0,
) -> list[ChatItem]:
    """
    Получает сообщения пользователя по курсу с пагинацией.

    :param session: SQLModel сессия
    :param user_id: ID пользователя
    :param course_uuid: UUID курса
    :param limit: Количество сообщений (по умолчанию 10)
    :param offset: Смещение (для пагинации)
    :return: Список сообщений в виде ChatItem
    """
    statement = select(MessageHistory).where(MessageHistory.user_id == user_id)
    statement = statement.order_by(desc(MessageHistory.assistant_send_at))
    statement = statement.limit(limit)
    statement = statement.offset(offset)

    results_raw = await session.exec(statement)
    results = results_raw.all()
    items = [
        ChatItem(
            user=row.user_text,
            assistant=row.assistant_text,
            assistant_send_at=row.assistant_send_at,
        )
        for row in results
    ]
    return sorted(items, key=lambda i: i.assistant_send_at)
