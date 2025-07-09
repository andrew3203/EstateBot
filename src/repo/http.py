import logging
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

import httpx

from src.utils.exceptions import APIException


logger = logging.getLogger(__name__)


def async_request():
    def decorator(func: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                async with httpx.AsyncClient() as client:
                    return await func(*args, client=client, **kwargs)
            except Exception as e:
                message = f"Failed to {func.__name__.upper()} response {str(e)}"
                logger.error(message, exc_info=True)
                raise APIException(msg=message) from e

        return wrapper

    return decorator


class HttpSource:
    """
    This class is used to make http requests
    """

    @async_request()
    async def get(self, headers: dict[str, str], url: str, **kwargs) -> dict:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.get(url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    @async_request()
    async def get_connent(self, headers: dict[str, str], url: str, **kwargs) -> Any:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.get(url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.content

    @async_request()
    async def post(
        self,
        headers: dict[str, str],
        url: str,
        data: dict[str, Any],
        **kwargs,
    ) -> dict:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.post(url, headers=headers, json=data, **kwargs)
        response.raise_for_status()
        return response.json()

    @async_request()
    async def post_content(
        self,
        headers: dict[str, str],
        url: str,
        data: dict[str, Any],
        **kwargs,
    ) -> Any:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.post(url, headers=headers, json=data, **kwargs)
        response.raise_for_status()
        return response.content

    @async_request()
    async def put(
        self,
        headers: dict[str, str],
        url: str,
        data: dict[str, Any],
        **kwargs,
    ) -> dict:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.put(url, headers=headers, json=data, **kwargs)
        response.raise_for_status()
        return response.json()

    @async_request()
    async def delete(self, headers: dict[str, str], url: str, **kwargs) -> dict:
        client: httpx.AsyncClient = kwargs.pop("client")
        response = await client.delete(url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
