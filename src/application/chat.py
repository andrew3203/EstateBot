from datetime import UTC, datetime
from src.application.intent_handler import IntentHandler
from src.application.ner_resolver import NERPromptResolver
from src.application.search import SearchEngine
from src.repo.history_queue import MessageHistoryQueue
from src.repo.intent_http import IntentHttp
from src.schema.ai_query import AIRequest
from src.service.history import UserHistory


class ChatUseCase:
    def __init__(self):
        self.http = IntentHttp()
        self.ner_resolver = NERPromptResolver()
        self.search_engine = SearchEngine()
        self.intent_handler = IntentHandler(
            ner_resolver=self.ner_resolver, search_engine=self.search_engine
        )

    async def retive_ansver(
        self,
        user_history: UserHistory,
        messages_queue: MessageHistoryQueue,
        data: AIRequest,
    ) -> tuple[str, dict]:
        history_str = await self.get_history_str(
            user_id=data.user_id,
            question=data.question,
            user_history=user_history,
        )

        intent_result = await self.http.get_intent(text=history_str)

        ner_result = None
        if intent_result.intent != "out_of_scope":
            ner_result = await self.http.get_ner(text=history_str)

        full_answer, aditional = await self.intent_handler.handle(
            intent=intent_result.intent, ner=ner_result
        )

        await user_history.update(
            user_id=data.user_id,
            answer=full_answer,
            question=data.question,
        )
        await messages_queue.add(
            user_id=data.user_id,
            user_text=data.question,
            assistant_text=full_answer,
            assistant_send_at=datetime.now(UTC),
        )

        return full_answer

    async def get_history_str(
        self,
        user_id: str,
        user_history: UserHistory,
        question: str,
    ) -> str:
        history = await user_history.get(user_id=user_id)
        result = ""
        for msg in history.data[-5:]:
            result += f"{msg.user}\n"
        return result + question
