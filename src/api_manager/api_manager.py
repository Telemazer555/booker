from pydantic import BaseModel
from requests import Response
from src.data_models.data_models import Credentials, HttpResponse
from functools import wraps
import inspect


def check_status_decorator(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Выполняем оригинальную функцию
        response = await func(*args, **kwargs)

        # Проверяем статус в зависимости от типа клиента
        if Credentials.CLIENT == "aiohttp":
            if response.status != 200:
                response.raise_for_status()
        elif Credentials.CLIENT == "httpx":
            if response.status_code != 200:
                response.raise_for_status()
        else:
            raise ValueError(f"Unsupported client type: {Credentials.CLIENT}")
        return response

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.status_code != 200:
            response.raise_for_status()
        return response

    # Определяем, асинхронная ли функция
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


class AsyncItemApiClient:
    def __init__(self, async_auth_session):
        self.async_auth_session = async_auth_session
        self.base_url = Credentials.BASE_URL

    @check_status_decorator
    async def as_get_items(self) -> HttpResponse:
        response = await self.async_auth_session.get(f"{self.base_url}/booking/")
        return response

    @check_status_decorator
    async def as_get_item(self, item_id: int) -> HttpResponse:
        response = await self.async_auth_session.get(f"{self.base_url}/booking/{item_id}")
        return response

    @check_status_decorator
    async def as_create_item(self, item_data: BaseModel) -> HttpResponse:
        response = await self.async_auth_session.post(
            f"{self.base_url}/booking",
            json=item_data.model_dump()
        )
        return response

    @check_status_decorator
    async def as_update_item(self, item_id: int, item_data: BaseModel) -> HttpResponse:
        response = await self.async_auth_session.put(
            f"{self.base_url}/booking/{item_id}",
            json=item_data.model_dump()
        )
        return response

    @check_status_decorator
    async def as_delete_item(self, item_id: int) -> HttpResponse:
        response = await self.async_auth_session.delete(f"{self.base_url}/booking/{item_id}")
        return response

    @staticmethod
    async def extract_response(response):
        if Credentials.CLIENT == "aiohttp":
            return await response.json()
        elif Credentials.CLIENT == "httpx":
            return response.json()
        else:
            raise ValueError(f"Unsupported client type: {Credentials.CLIENT}")


class ItemApiClient:
    def __init__(self, auth_session):
        self.auth_session = auth_session
        self.base_url = Credentials.BASE_URL

    @check_status_decorator
    def get_items(self) -> Response:
        response = self.auth_session.get(f"{self.base_url}/booking")
        return response

    @check_status_decorator
    def get_item(self, id_item: int) -> Response:
        response = self.auth_session.get(f"{self.base_url}/booking/{id_item}")
        return response

    @check_status_decorator
    def create_item(self, item_data: BaseModel) -> Response:
        response = self.auth_session.post(f"{self.base_url}/booking", json=item_data.model_dump())
        return response

    @check_status_decorator
    def update_item(self, item_id: int, item_data: BaseModel) -> Response:
        response = self.auth_session.put(f"{self.base_url}/booking/{item_id}", json=item_data.model_dump())
        return response

    @check_status_decorator
    def delete_item(self, item_id: int) -> Response:
        response = self.auth_session.delete(f"{self.base_url}/booking/{item_id}")
        return response
