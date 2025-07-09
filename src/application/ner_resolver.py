import random
from typing import Callable

from src.schema.schema import (
    AreaNER,
    LocationNER,
    NERResponse,
    PriceNER,
    PropertyNER,
    RoomNER,
)


class NERPromptResolver:
    def __init__(self):
        self.required_fields: dict[str, tuple[list[str], str]] = {
            "area": [
                "Какой метраж вас интересует?",
                "Уточните, пожалуйста, площадь недвижимости.",
            ],
            "price": ["Укажите диапазон цены.", "Какая стоимость для вас приемлема?"],
            "location": [
                "В каком районе или городе вы ищете?",
                "Уточните район, метро или город.",
            ],
            "property": [
                "Какой тип недвижимости вас интересует?",
                "Уточните тип объекта: квартира, дом и т.д.",
            ],
            "rooms": [
                "Сколько комнат должно быть в недвижимости?",
                "Уточните желаемое количество комнат.",
            ],
        }

    def get_missing_prompt(self, ner: NERResponse) -> str | None:
        for field, phrases in self.required_fields.items():
            value = getattr(ner, field, None)
            validator: Callable[[object], bool] = getattr(self, f"_{field}")
            if not validator(value):
                return random.choice(phrases)
        return None

    def _area(self, area: AreaNER | None) -> bool:
        return area is not None and (
            area.min_area is not None or area.max_area is not None
        )

    def _price(self, price: PriceNER | None) -> bool:
        return price is not None and (
            price.min_price is not None or price.max_price is not None
        )

    def _location(self, location: LocationNER | None) -> bool:
        return location is not None and any(
            getattr(location, attr) is not None
            for attr in ["district", "metro", "city"]
        )

    def _property(self, prop: PropertyNER | None) -> bool:
        return prop is not None and bool(prop.value)

    def _rooms(self, rooms: RoomNER | None) -> bool:
        return rooms is not None and rooms.count is not None
