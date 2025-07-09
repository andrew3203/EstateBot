from src.schema.schema import IntentResponse, NERResponse
from .http import HttpSource
from config.config import settings


class IntentHttp(HttpSource):
    async def get_intent(self, text: str) -> IntentResponse:
        result: dict = await self.post(
            url=f"{settings.INTENT_API_URL}/intent",
            headers={},
            data={"text": text},
        )
        return IntentResponse.model_validate(result)

    async def get_ner(self, text: str) -> NERResponse:
        result: dict = await self.post(
            url=f"{settings.INTENT_API_URL}/ner",
            headers={},
            data={"text": text},
        )
        return NERResponse.model_validate(result)
