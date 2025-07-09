from .http import HttpSource
from config.config import settings


class SearchHttp(HttpSource):
    async def search(self, params: dict, limit: int = 100) -> list[dict]:
        result: list[dict] = await self.get(
            url=f"{settings.QUERY_API_URL}", params=params
        )
        return result[:limit]
