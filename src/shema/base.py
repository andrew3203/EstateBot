"""Contains Base pydantic models"""

import logging
from datetime import UTC, datetime, time, timedelta
from typing import Any, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, ValidationError

from src.utils.exceptions import CoreException

Model = TypeVar("Model", bound=PydanticBaseModel)

logger = logging.getLogger(__name__)


def convert_datetime_to_gmt(dt: datetime) -> str:
    """From Datetime to str with timezone"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC) + timedelta(hours=3)

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


def convert_time_to_gmt(dt: time) -> str:
    """From time to str with timezone"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)

    return dt.strftime("%H:%M:%S%z")


class BaseModel(PydanticBaseModel):
    """BaseModel with new _model_config"""

    _model_config = ConfigDict(
        json_encoders={
            datetime: convert_datetime_to_gmt,
            time: convert_time_to_gmt,
        },
        populate_by_name=True,
    )

    def serializable_dict(self, **kwargs):
        """Return a dict which contains only serializable fields."""
        default_dict = self.model_dump(**kwargs)

        return jsonable_encoder(default_dict)

    @classmethod
    def model_validation(
        cls: type[Model],
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict[str, Any] | None = None,
    ) -> Model:
        try:
            result = cls.model_validate(
                obj=obj,
                strict=strict,
                from_attributes=from_attributes,
                context=context,
            )
            return result
        except ValidationError as e:
            logger.error(f"Data validation error {str(cls)}\n{str(e)}")
            raise CoreException(msg="Произошла внутренняя ошибка валлидации данных")

    @classmethod
    def model_validation_json(
        cls: type[Model],
        json_data: str | bytes | bytearray,
        *,
        strict: bool | None = None,
        context: dict[str, Any] | None = None,
    ) -> Model:
        try:
            result = cls.model_validate_json(
                json_data=json_data,
                strict=strict,
                context=context,
            )
            return result
        except ValidationError as e:
            logger.error(f"Data validation error {str(cls)}\n{str(e)}")
            raise CoreException(msg="Произошла внутренняя ошибка валлидации данных")
