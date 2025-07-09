from pydantic import Field

from .base import BaseModel


class ExceptionData(BaseModel):
    code: int = Field(description="Код ошибки")
    msg: str = Field(description="Сообщение ошибки")
    detail: str | None = Field(default=None, description="Доп. информация об ошибке")
    data: dict | None = Field(default=None, description="Доп информация об ошибке")
