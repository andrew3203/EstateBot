from datetime import datetime
from .base import BaseModel
from pydantic import Field


class AIQuery(BaseModel):
    question: str = Field(description="Users question")
    course_id: str = Field(description="Course id")
    course_name: str = Field(description="Course name")
    lesson_id: str | None = Field(description="Lesson id", default=None)
    lesson_name: str | None = Field(description="Lesson name", default=None)
    user_read_at: datetime = Field(description="User read message datetime in UTC")


class AIContextQuery(BaseModel):
    question: str = Field(description="Users question")
    course_id: str = Field(description="Course id")
