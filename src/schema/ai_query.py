from .base import BaseModel
from pydantic import Field


class AIRequest(BaseModel):
    user_id: str = Field(description="User id")
    question: str | None = Field(description="Users question")
    btn_key: str | None = Field(description="Uniqueue btn key", default=None)


class BTN(BaseModel):
    key: str = Field(description="Uniqueue btn key")
    label: str = Field(description="=Btn label")


class AIResponse(BaseModel):
    answer: str = Field(description="Model answer")
    aditional: dict = Field(description="Aditional data", default={})
    buttons: list[list[BTN]] = Field(description="btns", default=[])
