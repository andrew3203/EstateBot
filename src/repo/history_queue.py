import asyncio
from datetime import datetime

from src.db import get_transactional_session
from src.models.history import MessageHistory
from src.utils.singleton import SingletonMeta
import logging

logger = logging.getLogger(__name__)


class MessageHistoryQueue(metaclass=SingletonMeta):
    def __init__(self, flush_interval: int = 60):
        self._queue: list[MessageHistory] = []
        self._lock = asyncio.Lock()
        self._flush_interval = flush_interval
        self._stop_event = asyncio.Event()

        loop = asyncio.get_running_loop()
        self.task = loop.create_task(self._run())

    async def add(
        self,
        user_id: int,
        user_text: str,
        assistant_text: str,
        assistant_send_at: datetime,
    ):
        message = MessageHistory(
            user_id=user_id,
            user_text=user_text,
            assistant_text=assistant_text,
            assistant_send_at=assistant_send_at,
        )
        async with self._lock:
            self._queue.append(message)

    async def _flush(self):
        async with self._lock:
            messages_to_save = self._queue[:]

            if not messages_to_save:
                return

            async with get_transactional_session() as session:
                try:
                    session.add_all(messages_to_save)
                    await session.commit()
                    self._queue.clear()
                    logger.info(f"Created {len(messages_to_save)} new messages")
                except Exception as e:
                    await session.rollback()
                    logger.error(f"Faild to create save message {e}", exc_info=True)

    async def _run(self):
        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(self._flush_interval)
                await self._flush()
        except asyncio.CancelledError:
            logger.info("Flush task cancelled")

    async def stop(self):
        self._stop_event.set()
        self.task.cancel()
        await self._flush()
