from pydantic import BaseModel
from requests import Response
from src.data_models.data_models import Credentials
from typing import Callable
from functools import wraps
import inspect
from aiohttp import ClientResponse
from httpx import Response as HttpxResponse

# class ItemApiClient:
#     def __init__(self, auth_session):
#         self.auth_session = auth_session
#         self.base_url = Credentials.BASE_URL  # Можно также передавать в конструктор, если он может меняться
#
#     def get_items(self) -> Response:
#         """Отправляет запрос на получение списка items."""
#         response = self.auth_session.get(f"{self.base_url}/booking")
#         if response.status_code != 200:
#             response.raise_for_status()
#         return response
#
#     def get_item(self, id_item: int) -> Response:
#         """Отправляет запрос на получение списка items."""
#         response = self.auth_session.get(f"{self.base_url}/booking/{id_item}")
#         if response.status_code != 200:
#             response.raise_for_status()
#         return response
#
#     def create_item(self, item_data: BaseModel) -> Response:
#         response = self.auth_session.post(f"{self.base_url}/booking", json=item_data.model_dump())
#         if response.status_code != 200:
#             response.raise_for_status()
#         return response  # возвращаем response в model_dump
#
#     def update_item(self, item_id: int, item_data: BaseModel) -> Response:
#         """Отправляет запрос на обновление item."""
#         response = self.auth_session.put(f"{self.base_url}/booking/{item_id}", json=item_data.model_dump())
#         if response.status_code != 200:
#             response.raise_for_status()
#         return response
#
#     def delete_item(self, item_id: int) -> Response:
#         """Отправляет запрос на удаление item."""
#         response = self.auth_session.delete(f"{self.base_url}/booking/{item_id}")
#
#         if response.status_code != 200:  # В REST для DELETE часто возвращают 204 No Content или 200 OK
#             response.raise_for_status()
#         # Для DELETE часто нечего возвращать из тела, либо можно вернуть статус-код или сам response
#         return response  # или response.status_code
#
#
# class AsyncItemApiClient:
#
#     def __init__(self, async_auth_session):
#         self.async_auth_session = async_auth_session
#         self.base_url = Credentials.BASE_URL
#
#     async def as_get_items(self) -> Response:
#         response = await self.async_auth_session.get(f"{self.base_url}/booking/")
#         if Credentials.CLIENT == "aiohttp":
#             if response.status != 200:
#                 response.raise_for_status()
#         elif Credentials.CLIENT == "httpx":
#             if response.status_code != 200:
#                 response.raise_for_status()
#         return response
#
#     async def as_get_item(self, item_id: int) -> Response:
#         response = await self.async_auth_session.get(f"{self.base_url}/booking/{item_id}")
#         if Credentials.CLIENT == "aiohttp":
#             if response.status != 200:
#                 response.raise_for_status()
#         elif Credentials.CLIENT == "httpx":
#             if response.status_code != 200:
#                 response.raise_for_status()
#         return response
#
#     async def as_create_item(self, item_data: BaseModel) -> Response:
#         response = await  self.async_auth_session.post(f"{self.base_url}/booking", json=item_data.model_dump())
#         if Credentials.CLIENT == "aiohttp":
#             if response.status != 200:
#                 response.raise_for_status()
#         elif Credentials.CLIENT == "httpx":
#             if response.status_code != 200:
#                 response.raise_for_status()
#         return response
#
#     async def as_update_item(self, item_id: int, item_data: BaseModel) -> Response:
#         response = await self.async_auth_session.put(f"{self.base_url}/booking/{item_id}", json=item_data.model_dump())
#         if Credentials.CLIENT == "aiohttp":
#             if response.status != 200:
#                 response.raise_for_status()
#         elif Credentials.CLIENT == "httpx":
#             if response.status_code != 200:
#                 response.raise_for_status()
#         return response
#
#     async def as_delete_item(self, item_id: int) -> Response:
#         response = await self.async_auth_session.delete(f"{self.base_url}/booking/{item_id}")
#         if Credentials.CLIENT == "aiohttp":
#             if response.status != 200:
#                 response.raise_for_status()
#         elif Credentials.CLIENT == "httpx":
#             if response.status_code != 200:
#                 response.raise_for_status()
#         return response
#

HttpResponse = ClientResponse | HttpxResponse

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

        if Credentials.CLIENT == "aiohttp":
            if response.status != 200:
                response.raise_for_status()
        elif Credentials.CLIENT == "httpx":
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
