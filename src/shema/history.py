from datetime import datetime
from .base import BaseModel
from pydantic import Field


class ChatItem(BaseModel):
    user: str = Field(description="User question")
    user_read_at: datetime = Field(description="User read datetime")
    assistant: str = Field(description="Assistent answer")
    assistent_send_at: datetime = Field(description="Assistent read datetime")


class HostoryModel(BaseModel):
    data: list[ChatItem] = Field(description="Users question")
    spent: int = Field(description="Nummber of spent questions")
    limit: int = Field(description="Nummber of limit questions")
