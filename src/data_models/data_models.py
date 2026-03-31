from typing import Optional, Type
from faker import Faker
from pydantic import BaseModel, ValidationError, Field
from requests import Response
from pathlib import Path
from aiohttp import ClientResponse
from httpx import Response as HttpxResponse

import pytest
import json
import os
import dotenv

fake = Faker()
dotenv.load_dotenv()
HttpResponse = ClientResponse | HttpxResponse


class Credentials:
    CLIENT = None

    # Сначала проверяем наличие .env файла
    if not Path('.env').exists():
        print("\n" + "=" * 190)
        print("❌ ОШИБКА: Файл .env не найден")
        print("=" * 190)
        print("🔧 Создайте файл .env с конфигурацией API")
        print("📋 Инструкция в README.md")
        print("=" * 190 + "\n")
        raise FileNotFoundError("Необходимо создать файл .env с конфигурацией API")

    # Проверяем HEADERS
    try:
        headers_raw = os.environ.get('HEADERS')
        if headers_raw is None or headers_raw.strip() == "":
            raise ValueError("HEADERS не найдена или пуста в .env файле")
        HEADERS = json.loads(headers_raw)
    except (json.JSONDecodeError, ValueError) as e:
        print("\n" + "=" * 190)
        print(f"❌ ОШИБКА ЗАГРУЗКИ HEADERS: {e}")
        print("=" * 190)
        print("🔧 ПРОВЕРЬТЕ:")
        print("  1. Что переменная HEADERS существует в файле .env")
        print("  2. Что значение HEADERS не пустое")
        print("  3. Что значение HEADERS является корректным JSON")
        print("\n📋 Пример корректного HEADERS:")
        print('  HEADERS={"Content-Type": "application/json", "Accept": "application/json"}')
        print("=" * 190 + "\n")
        raise

    # Проверяем BASE_URL
    BASE_URL = os.environ.get('BASE_URL')
    if BASE_URL is None or BASE_URL.strip() == "":
        print("\n" + "=" * 190)
        print("❌ ОШИБКА: BASE_URL не найдена или пуста в .env файле")
        print("=" * 190)
        print("🔧 Добавьте BASE_URL в файл .env")
        print("\n📋 Пример:")
        print('  BASE_URL=https://api.example.com/v1')
        print("=" * 190 + "\n")
        raise ValueError("Необходимо указать BASE_URL в .env файле")
    else:
        print(f"✓ BASE_URL загружен: {BASE_URL}")

    # Проверяем JSON_BODY
    try:
        json_body_raw = os.environ.get('JSON_BODY')
        if json_body_raw is None or json_body_raw.strip() == "":
            raise ValueError("JSON_BODY не найдена или пуста в .env файле")
        JSON_BODY = json.loads(json_body_raw)
    except (json.JSONDecodeError, ValueError) as e:
        print("\n" + "=" * 190)
        print(f"❌ ОШИБКА ЗАГРУЗКИ JSON_BODY: {e}")
        print("=" * 190)
        print("🔧 ПРОВЕРЬТЕ:")
        print("  1. Что переменная JSON_BODY существует в файле .env")
        print("  2. Что значение JSON_BODY не пустое")
        print("  3. Что значение JSON_BODY является корректным JSON")
        print("\n📋 Пример корректного JSON_BODY:")
        print('  JSON_BODY={"username": "admin", "password": "password123"}')
        print("=" * 190 + "\n")
        raise


class BookingDatesDataModel(BaseModel):
    checkin: str
    checkout: str

    @classmethod
    def fake_checkdates(cls):
        return cls(
            checkin=fake.date(),
            checkout=fake.date()
        )


class BaseBookingSchemaDataModel(BaseModel):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDatesDataModel
    additionalneeds: Optional[str] = None


class CreateUserSchemaDataModel(BaseModel):
    bookingid: int
    booking: BaseBookingSchemaDataModel


class BookingResponseDataModel(BaseModel):
    firstname: str = Field(default_factory=fake.first_name)
    lastname: str = Field(default_factory=fake.last_name)
    totalprice: int = Field(default_factory=lambda: fake.random_int(min=100, max=10000))
    depositpaid: bool = Field(default_factory=fake.boolean)
    bookingdates: BookingDatesDataModel = Field(default_factory=BookingDatesDataModel.fake_checkdates)
    additionalneeds: str | None = Field(
        default_factory=lambda: fake.random_element(elements=("breakfast", "dinner", "supper", None))
    )


def validate_response(response: Response,
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


async def validate_response_as(
        response,
        model: Type[BaseModel],
        expected_status: int = 200,
        expected_data: dict | None = None
) -> BaseModel:
    # определяем тип response и получаем данные
    if hasattr(response, 'status') and hasattr(response, 'json'):
        # aiohttp ClientResponse
        status = response.status
        try:
            data = await response.json() if callable(getattr(response, 'json', None)) else response
        except Exception as e:
            pytest.fail(f"Ошибка парсинга JSON из aiohttp response: {e}")

    elif hasattr(response, 'status_code') and hasattr(response, 'json'):
        # httpx Response
        status = response.status_code
        try:
            data = response.json() if callable(getattr(response, 'json', None)) else response
        except Exception as e:
            pytest.fail(f"Ошибка парсинга JSON из httpx response: {e}")

    elif isinstance(response, dict):
        # если response уже словарь
        status = expected_status  # или нужно как-то получить статус из словаря?
        data = response

    else:
        raise TypeError(f"Неподдерживаемый тип response: {type(response)}")

    # проверка статуса
    if status != expected_status:
        pytest.fail(f"Expected status {expected_status}, got {status}")

    # Pydantic валидация
    try:
        parsed = model(**data)
    except ValidationError as e:
        pytest.fail(f"Pydantic валидация не прошла:\n{e}")

    # сравнение ожидаемых данных
    if expected_data:
        expected_model = model(**expected_data)

        # Сравниваем только те поля, которые есть в expected_data
        parsed_dict = parsed.model_dump(exclude_unset=True)
        expected_dict = expected_model.model_dump(exclude_unset=True)

        # Проверяем только указанные поля
        for key in expected_data.keys():
            if key not in parsed_dict or parsed_dict[key] != expected_dict.get(key):
                pytest.fail(
                    f"Данные ответа не совпадают по полю '{key}':\n"
                    f"Expected: {expected_dict.get(key)}\n"
                    f"Actual:   {parsed_dict.get(key)}"
                )

    return parsed
