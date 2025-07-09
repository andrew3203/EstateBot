import typing
from datetime import date, datetime
from decimal import Decimal

import orjson
from fastapi import Request


class json:
    @classmethod
    def dumps(cls, data, compact=True) -> str:
        return cls.dumpb(data, compact).decode("utf-8")

    @classmethod
    def dumpb(cls, data, compact=True) -> bytes:
        return orjson.dumps(
            data,
            default=cls.jsonSerialize,
            option=orjson.OPT_NON_STR_KEYS
            | orjson.OPT_PASSTHROUGH_SUBCLASS
            | (orjson.OPT_INDENT_2 if __debug__ and not compact else 0),
        )

    @classmethod
    def loads(cls, src: str | bytes):
        return orjson.loads(src)

    @classmethod
    def jsonSerialize(cls, o):
        if isinstance(o, datetime):
            return o.isoformat(sep="T", timespec="milliseconds")
        elif isinstance(o, date):
            return o.strftime("%Y-%m-%d")
        elif isinstance(o, Decimal):
            return float(o)
        elif isinstance(o, set):
            return list(o)
        else:
            try:
                return o.__repr__()
            except Exception:
                return "<%s>" % type(o)

    async def _request_json(self) -> typing.Any:
        """Функция для подмены оригинальной функции json в fastapi.Request"""
        if not hasattr(self, "_json"):
            body = await self.body()  # type: ignore
            self._json = orjson.loads(body)
        return self._json

    @classmethod
    def set_fastapi_json(cls):
        setattr(Request, "json", cls._request_json)  # noqa: B010


__all__ = ["json"]
