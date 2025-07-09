import os
import time
import threading
import queue
import uuid
from collections import OrderedDict
from typing import Any, Literal

from redis import Redis, ConnectionPool
from src.json import json

from config.config import settings
from src.utils.singleton import SingletonMeta

import logging

logger = logging.getLogger(__name__)


class ThreadSafeLRUCache(metaclass=SingletonMeta):
    def __init__(self, max_age: int, maxsize: int, redis_key="lru_cache"):
        self.cache: OrderedDict[str | int, Any] = OrderedDict()
        self.max_age = max_age
        self.maxsize = maxsize
        self.lock = threading.Lock()
        self.instance_id = self.__generate_instance_id()

        redis_pool = ConnectionPool.from_url(
            url=settings.REDIS_URL,
            max_connections=5,
            socket_timeout=30,
            db=0,
            encoding="utf-8",
            socket_connect_timeout=20,
            health_check_interval=30,
            retry_on_timeout=True,
            decode_responses=True,
        )
        self.redis = Redis(connection_pool=redis_pool)
        self.redis_storage_key = f"{redis_key}_storage"
        self.redis_stream_key = f"{redis_key}_stream"

        self._load_all_from_redis()

        self.stop_event = threading.Event()

        self.task_queue: queue.Queue[
            tuple[Literal["set", "delete"], str | int, Any | None]
        ] = queue.Queue()

        self.sync_thread = threading.Thread(target=self._background_sync, daemon=True)
        self.sync_thread.start()

        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def __generate_instance_id(self):
        pod_name = os.getenv("HOSTNAME", "unknownpod")
        pid = os.getpid()
        random_part = str(uuid.uuid4())
        timestamp = int(time.time() * 1e6) % 1000
        return f"{pod_name}-{pid}-{random_part}-{timestamp}"

    def _load_all_from_redis(self):
        try:
            cursor = 0
            while True:
                cursor, data = self.redis.hscan(
                    self.redis_storage_key, cursor=cursor, count=100
                )
                with self.lock:
                    now = time.time()
                    for key, raw_val in data.items():
                        try:
                            value, timestamp = json.loads(raw_val)
                            if now - timestamp < self.max_age:
                                self.cache[key] = (value, timestamp)
                        except Exception as e:
                            logger.error(f"JSON decode error on key={key}: {e}")
                if cursor == 0:
                    break
        except Exception as e:
            logger.error(f"Redis HSCAN load error: {e}")

    def _save_item_to_redis(self, key: str | int, value: Any) -> None:
        packed_value = json.dumps([value, time.time()])
        self.task_queue.put(("set", key, packed_value))

    def _delete_item_from_redis(self, key: str | int) -> None:
        self.task_queue.put(("delete", key, None))

    def _worker_loop(self):
        while not self.stop_event.is_set():
            try:
                task = self.task_queue.get(timeout=1)
            except queue.Empty:
                continue

            op, key, value = task
            logger.info(
                "NEW ACTION",
                extra={
                    "op": op,
                    "key": key,
                    "from": self.instance_id,
                },
            )
            pipe = self.redis.pipeline()
            try:
                pipe.reset()
                if op == "set":
                    pipe.hset(self.redis_storage_key, key, value)
                elif op == "delete":
                    pipe.hdel(self.redis_storage_key, key)
                pipe.xadd(
                    self.redis_stream_key,
                    {
                        "op": op,
                        "key": key,
                        "value": value or "",
                        "sender": self.instance_id,
                    },
                    maxlen=1000,
                    approximate=True,
                )
                pipe.execute()
            except Exception as e:
                logger.error(f"Redis worker error on {op} key={key}: {e}")
            finally:
                self.task_queue.task_done()

    def _background_sync(self):
        while not self.stop_event.is_set():
            try:
                entries = self.redis.xread(
                    {self.redis_stream_key: "$"},
                    count=100,
                    block=1000,
                )

                for _, messages in entries:
                    with self.lock:
                        now = time.time()
                        for msg_id, fields in messages:
                            op = fields["op"]
                            key = fields["key"]
                            value = fields.get("value")
                            sender = fields.get("sender")
                            if sender == self.instance_id:
                                continue

                            logger.info(
                                "RECIVE ACTION",
                                extra={
                                    "op": op,
                                    "key": key,
                                    "to": self.instance_id,
                                    "from": sender,
                                },
                            )

                            try:
                                if op == "set" and value:
                                    unpacked_value, timestamp = json.loads(value)
                                    if now - timestamp < self.max_age:
                                        self.cache[key] = (unpacked_value, timestamp)
                                    else:
                                        self.cache.pop(key, None)
                                elif op == "delete":
                                    self.cache.pop(key, None)
                            except Exception as e:
                                logger.error(f"Failed to process stream message: {e}")

            except Exception as e:
                logger.error(f"Redis stream read error: {e}")
                time.sleep(5)

    def stop(self):
        self.stop_event.set()
        self.sync_thread.join()
        self.worker_thread.join()

    def get(self, key: str | int) -> Any | None:
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                now = time.time()
                if now - timestamp < self.max_age:
                    self.cache.move_to_end(key)
                    logger.info(
                        "GET DATA",
                        extra={
                            "key": key,
                            "from": self.instance_id,
                        },
                    )
                    return value
                else:
                    del self.cache[key]
                    self._delete_item_from_redis(key)
            return None

    def set(self, key: str | int, value: Any) -> None:
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = (value, time.time())
            if len(self.cache) > self.maxsize:
                old_key, _ = self.cache.popitem(last=False)
                self._delete_item_from_redis(old_key)
            self._save_item_to_redis(key, value)
