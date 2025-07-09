from typing import Literal
from .base import BaseModel
from pydantic import Field


class IntentResponse(BaseModel):
    intent: Literal["out_of_scope", "buy_property"] = Field(description="intent")
    score: float = Field(description="Intent score")


class AreaNER(BaseModel):
    min_area: int | None = Field(description="min_area")
    max_area: int | None = Field(description="max_area")


class PriceNER(BaseModel):
    min_price: int | None = Field(description="min_price")
    max_price: int | None = Field(description="max_price")


class PropertyNER(BaseModel):
    value: str = Field(description="Value")


class LocationNER(BaseModel):
    district: str | None = Field(description="district")
    metro: str | None = Field(description="metro")
    city: str | None = Field(description="city")


class RoomNER(BaseModel):
    count: int | None = Field(description="count")


class NERResponse(BaseModel):
    area: AreaNER | None = Field(description="Area result")
    price: PriceNER | None = Field(description="Price result")
    location: LocationNER | None = Field(description="Location result")
    property: PropertyNER | None = Field(description="Property result")
    rooms: RoomNER | None = Field(description="room result")
