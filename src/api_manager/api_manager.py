import pytest

from pydantic import BaseModel, ValidationError
from requests import Response
from typing import Type
from src.data_models.data_models import Credentials


class ItemApiClient:
    def __init__(self, auth_session):
        self.auth_session = auth_session
        self.base_url = Credentials.BASE_URL  # Можно также передавать в конструктор, если он может меняться

    def get_items(self) -> Response:
        """Отправляет запрос на получение списка items."""
        response = self.auth_session.get(f"{self.base_url}/booking")
        if response.status_code != 200:
            response.raise_for_status()
        return response

    def get_item(self, id_item: int) -> Response:
        """Отправляет запрос на получение списка items."""
        response = self.auth_session.get(f"{self.base_url}/booking/{id_item}")
        if response.status_code != 200:
            response.raise_for_status()
        return response

    def create_item(self, item_data: BaseModel) -> Response:
        response = self.auth_session.post(f"{self.base_url}/booking", json=item_data.model_dump())
        if response.status_code != 200:
            response.raise_for_status()
        return response  # возвращаем response в model_dump

    def update_item(self, item_id: int, item_data: BaseModel) -> Response:
        """Отправляет запрос на обновление item."""
        response = self.auth_session.put(f"{self.base_url}/booking/{item_id}", json=item_data.model_dump())
        if response.status_code != 200:
            response.raise_for_status()
        return response

    def delete_item(self, item_id: int) -> Response:
        """Отправляет запрос на удаление item."""
        response = self.auth_session.delete(f"{self.base_url}/booking/{item_id}")

        if response.status_code != 200:  # В REST для DELETE часто возвращают 204 No Content или 200 OK
            response.raise_for_status()
        # Для DELETE часто нечего возвращать из тела, либо можно вернуть статус-код или сам response
        return response  # или response.status_code


class AsyncItemApiClient:

    def __init__(self, async_auth_session):
        self.async_auth_session = async_auth_session
        self.base_url = Credentials.BASE_URL

    async def as_get_items(self) -> Response:
        response = await self.async_auth_session.get(f"{self.base_url}/booking/")
        if Credentials.CLIENT == "aiohttp":
            if response.status != 200:
                response.raise_for_status()
        elif Credentials.CLIENT == "httpx":
            if response.status_code != 200:
                response.raise_for_status()
        return response

    async def as_get_item(self, item_id: int) -> Response:
        response = await self.async_auth_session.get(f"{self.base_url}/booking/{item_id}")
        if Credentials.CLIENT == "aiohttp":
            if response.status != 200:
                response.raise_for_status()
        elif Credentials.CLIENT == "httpx":
            if response.status_code != 200:
                response.raise_for_status()
        return response

    async def as_create_item(self, item_data: BaseModel) -> Response:
        response = await  self.async_auth_session.post(f"{self.base_url}/booking", json=item_data.model_dump())
        if Credentials.CLIENT == "aiohttp":
            if response.status != 200:
                response.raise_for_status()
        elif Credentials.CLIENT == "httpx":
            if response.status_code != 200:
                response.raise_for_status()
        return response

    async def as_update_item(self, item_id: int, item_data: BaseModel) -> Response:
        response = await self.async_auth_session.put(f"{self.base_url}/booking/{item_id}", json=item_data.model_dump())
        if Credentials.CLIENT == "aiohttp":
            if response.status != 200:
                response.raise_for_status()
        elif Credentials.CLIENT == "httpx":
            if response.status_code != 200:
                response.raise_for_status()
        return response

    async def as_delete_item(self, item_id: int) -> Response:
        response = await self.async_auth_session.delete(f"{self.base_url}/booking/{item_id}")
        if Credentials.CLIENT == "aiohttp":
            if response.status != 200:
                response.raise_for_status()
        elif Credentials.CLIENT == "httpx":
            if response.status_code != 200:
                response.raise_for_status()
        return response


class Validator:

    def validate_response(self, response: Response,
                          model: Type[BaseModel],
                          expected_status: int = 200,
                          expected_data: dict | None = None
                          ) -> BaseModel:
        if response.status_code != expected_status:
            pytest.fail(f"Expected status {expected_status}, got {response.status_code}: {response.text}")
        try:
            data = response.json()
        except Exception as e:
            pytest.fail(f"Ошибка парсинга JSON: {e}\nResponse: {response.text}")
        try:
            parsed = model(**data)
        except ValidationError as e:
            pytest.fail(f"Pydantic валидация не прошла:\n{e}")
        if expected_data:
            expected_model = model(**expected_data)
            if parsed.model_dump(exclude_unset=True) != expected_model.model_dump(exclude_unset=True):
                pytest.fail(
                    f"Данные ответа не совпадают с ожидаемыми:\n"
                    f"Expected: {expected_model.model_dump()}\n"
                    f"Actual:   {parsed.model_dump()}"
                )

        return parsed

    async def validate_response_aiohttp(self, response: Response,
                                        model: Type[BaseModel],
                                        expected_status: int = 200,
                                        expected_data: dict | None = None
                                        ) -> BaseModel:
        if response.status != expected_status:
            raise ValueError(f"Expected status {expected_status}, got {response.status}")
        try:
            data = await response.json()
        except Exception as e:
            pytest.fail(f"Ошибка парсинга JSON: {e}\nResponse: {response.text}")
        try:
            parsed = model(**data)
        except ValidationError as e:
            pytest.fail(f"Pydantic валидация не прошла:\n{e}")
        if expected_data:
            expected_model = model(**expected_data)
            if parsed.model_dump(exclude_unset=True) != expected_model.model_dump(exclude_unset=True):
                pytest.fail(
                    f"Данные ответа не совпадают с ожидаемыми:\n"
                    f"Expected: {expected_model.model_dump()}\n"
                    f"Actual:   {parsed.model_dump()}"
                )
        return parsed
