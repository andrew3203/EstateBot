from sqlmodel import Session, select
from sqlmodel import desc
from src.models.history import MessageHistory
from src.shema.history import ChatItem


def get_user_messages_paginated(
    session: Session,
    user_id: int,
    course_uuid: str | None = None,
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
    if course_uuid:
        statement = statement.where(MessageHistory.course_uuid == course_uuid)

    statement = statement.order_by(desc(MessageHistory.user_read_at))
    statement = statement.limit(limit)
    statement = statement.offset(offset)

    results = session.exec(statement).all()

    items = [
        ChatItem(
            user=row.user_text,
            user_read_at=row.user_read_at,
            assistant=row.assistant_text,
            assistent_send_at=row.assistent_send_at,
        )
        for row in results
    ]
    return sorted(items, key=lambda i: i.assistent_send_at)
