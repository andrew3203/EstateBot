from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field, SQLModel

from src.db import metadata


class MessageHistory(SQLModel, table=True, metadata=metadata):
    __tablename__ = "message_history"

    id: int | None = Field(description="id", primary_key=True, default=None)
    user_id: int = Field(description="User id", index=True)
    course_uuid: str = Field(description="Course uuid")
    user_text: str = Field(description="User question text")
    assistant_text: str = Field(description="User question text")

    user_read_at: datetime = Field(
        description="Date user read the assistant text",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
    assistent_send_at: datetime = Field(
        description="Date assistant read users question",
        sa_column=sa.Column(sa.DateTime(timezone=True), nullable=False),
    )
