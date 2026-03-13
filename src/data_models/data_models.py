from pydantic import Field
from typing import Optional
from faker import Faker
from pydantic import BaseModel, ValidationError
from requests import Response
from typing import Type
from pathlib import Path
import pytest
import json
import os
import dotenv

fake = Faker()
dotenv.load_dotenv()


# class Credentials:
#
#     CLIENT = None
#
#     try:
#         HEADERS = os.environ.get('HEADERS')
#         HEADERS = json.loads(HEADERS)
#         BASE_URL = os.environ.get('BASE_URL')
#         JSON_BODY = os.environ.get('JSON_BODY')
#         JSON_BODY = json.loads(JSON_BODY)
#
#     except ValueError:
#         print("Заполните .env")

class Credentials:
    CLIENT = None

    # Сначала проверяем наличие .env файла
    if not Path('.env').exists():
        raise FileNotFoundError(
            "Необходимо создать файл .env с конфигурацией API проверьте заполненность файла, инструкция в README.md")

    # Загружаем и проверяем HEADERS
    try:
        headers_raw = os.environ.get('HEADERS')
        if headers_raw is None:
            raise ValueError("HEADERS не найдена в .env файле")
        HEADERS = json.loads(headers_raw)
    except (json.JSONDecodeError, ValueError) as e:
        print("\n" + "=" * 190)
        print(f"  ❌ Проверьте заполненность файла .env инструкция в README.md")
        print("=" * 190 + "\n")
        raise

    # Проверяем BASE_URL
    BASE_URL = os.environ.get('BASE_URL')
    if BASE_URL is None:
        # print("\n" + "=" * 70)
        # print("❌ ОШИБКА: BASE_URL не найдена в .env файле")
        # print("=" * 70)
        # print("🔧 Добавьте BASE_URL в файл .env")
        # print("\n📋 Пример:")
        # print('  BASE_URL=https://api.example.com/v1')
        # print("=" * 70 + "\n")
        raise ValueError("Необходимо указать BASE_URL в .env файле")
    else:
        print(f"✓ BASE_URL загружен: {BASE_URL}")  # Опционально: для отладки

    # Загружаем и проверяем JSON_BODY
    try:
        json_body_raw = os.environ.get('JSON_BODY')
        if json_body_raw is None:
            raise ValueError("JSON_BODY не найдена в .env файле")
        JSON_BODY = json.loads(json_body_raw)
        print("✓ JSON_BODY успешно загружено")  # Опционально: для отладки
    except (json.JSONDecodeError, ValueError) as e:
        # print("\n" + "=" * 70)
        # print(f"❌ ОШИБКА ЗАГРУЗКИ JSON_BODY: {e}")
        # print("=" * 70)
        # print("🔧 ПРОВЕРЬТЕ:")
        # print("  1. Что переменная JSON_BODY существует в файле .env")
        # print("  2. Что значение JSON_BODY является корректным JSON")
        # print("\n📋 Пример корректного JSON_BODY:")
        # print('  JSON_BODY={"username": "admin", "password": "password123"}')
        # print("=" * 70 + "\n")
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
    bookingdates: dict
    bookingdates: BookingDatesDataModel
    additionalneeds: Optional[str] = None


class BookingResponseDataModel(BaseModel):
    firstname: str = Field(default_factory=fake.first_name)
    lastname: str = Field(default_factory=fake.last_name)
    totalprice: int = Field(default_factory=lambda: fake.random_int(min=100, max=10000))
    depositpaid: bool = Field(default_factory=fake.boolean)
    bookingdates: BookingDatesDataModel = Field(default_factory=BookingDatesDataModel.fake_checkdates)
    additionalneeds: str | None = Field(
        default_factory=lambda: fake.random_element(elements=("breakfast", "dinner", "supper", None))
    )


class CreateUserSchemaDataModel(BaseModel):
    bookingid: int
    booking: BaseBookingSchemaDataModel


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


async def validate_response_aiohttp(response: Response,
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
