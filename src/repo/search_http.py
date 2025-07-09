from src.schema.schema import IntentResponse, NERResponse
from .http import HttpSource
from config.config import settings


class SearchHttp(HttpSource):
    async def search(self, data: NERResponse) -> list[dict]:
        result: dict = await self.post(url=f"{settings.INTENT_API_URL}/intent")
        return IntentResponse.model_validate(result)
