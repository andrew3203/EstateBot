from pydantic import AliasChoices, Field

from .base import BaseModel


class UserTariff(BaseModel):
    id: int = Field(alias="t", description="Уникальный номер тарифа")
    flow: int = Field(default=1, alias="f", description="Номер потока")


class User(BaseModel):
    id: int = Field(
        description="User ID",
        validation_alias=AliasChoices("U", "id"),
    )
    session: int = Field(description="Session", alias="S", ge=0)
    sub: str = Field(description="sub")
    lang: str = Field(description="lang", default="RU")
    roles: dict[str, int | str] = Field(
        description="Роль данного пользователя", alias="acc", default={}
    )
    tariffs: list[UserTariff] = Field(
        description="Список доступный тарифов", alias="tariff", default=[]
    )
