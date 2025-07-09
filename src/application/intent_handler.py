from src.application.ner_resolver import NERPromptResolver
from src.application.search import SearchEngine
from src.schema.schema import NERResponse


class IntentHandler:
    def __init__(self, ner_resolver: NERPromptResolver, search_engine: SearchEngine):
        self.ner_resolver = ner_resolver
        self.search_engine = search_engine

    async def handle(self, intent: str, ner: NERResponse | None) -> str:
        if intent == "out_of_scope":
            return "Я вас не понимаю, переформулируйте вопрос. Я могу помочь с покупкой недвижимости."

        if intent == "buy_property":
            if ner is None:
                return "Не удалось извлечь параметры. Повторите, пожалуйста."

            missing_prompt = self.ner_resolver.get_missing_prompt(ner)
            if missing_prompt:
                return missing_prompt

            # все параметры есть — выполняем поиск
            results = await self.search_engine.search(ner)
            return self.search_engine.format_results(results)

        return "Неизвестный запрос. Попробуйте переформулировать."
