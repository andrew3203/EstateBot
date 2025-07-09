from src.utils.exceptions import APIException
from .http import HttpSource
from config.config import settings


class SearchHttp(HttpSource):
    async def search(self, params: dict, limit: int = 100) -> list[dict]:
        result: list[dict] = await self.get(
            url=f"{settings.QUERY_API_URL}", headers={}, params=params
        )
        if result.get("status") == "ok":
            return result["data"][:limit]
        raise APIException(msg="Faild to get property")
