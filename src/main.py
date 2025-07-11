from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.application.chat import ChatUseCase
from src.repo.history_queue import MessageHistoryQueue
from src.routers import router
from src.service.history import UserHistory
from src.utils.exceptions import BaseException
from src.utils.cache import SafeLRUCache


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = SafeLRUCache(max_age=60 * 5, maxsize=10_000)
    app.state.user_history = UserHistory(cache=cache)
    app.state.messages_queue = MessageHistoryQueue()
    app.state.chat = ChatUseCase()

    yield

    cache.stop()
    await app.state.messages_queue.stop()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(BaseException)
async def core_error_handler(request: Request, exc: BaseException) -> ORJSONResponse:
    if exc.code == status.HTTP_400_BAD_REQUEST:
        detail = "Произошел некорректный запрос. Попробуйте заново."
    elif exc.code == status.HTTP_403_FORBIDDEN:
        detail = "У вас нет доступа к ресурсу."
    elif exc.code == status.HTTP_404_NOT_FOUND:
        detail = "Обьект не найден."
    else:
        detail = f"Произошла внутренняя ошибка. Код: {exc.code}."
    return ORJSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "msg": exc.msg,
            "detail": detail,
            "data": exc.data,
        },
    )


app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["*"],
)
