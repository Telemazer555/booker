import pytest
import requests
import httpx
import pytest_asyncio
import aiohttp

from src.api_manager.api_manager import ItemApiClient, AsyncItemApiClient
from src.data_models.data_models import Credentials
from src.scenarios.scenarios import ItemScenarios, ItemScenariosAsync

##########################################################################################
"""Запуск тестов через флags: --client httpx или --client aiohttp или --client requests"""


def pytest_addoption(parser):
    parser.addoption(
        "--client",
        action="store",
        default="httpx",
        choices=["httpx", "requests", "aiohttp"],
        help="""
            Выбор HTTP клиента для тестов:
            - httpx: для синхронных и асинхронных тестов
            - requests: только для синхронных тестов
            - aiohttp: только для асинхронных тестов
            По умолчанию: httpx
            """
    )


@pytest.fixture(autouse=True, scope="session")
def set_client(request):
    client = request.config.getoption("--client")
    Credentials.CLIENT = client
    return client


##########################################################################################
"""SYNC"""


@pytest.fixture(scope='session')
def auth_session(set_client):
    param = set_client
    print(f"\n🔧 Запуск с клиентом: {param}")
    if param == "httpx":
        session = httpx.Client(verify=False)
    elif param == "requests":
        session = requests.session()
        session.verify = False
    else:
        raise ValueError(f"Неизвестный клиент: {param}")
    session.headers.update(Credentials.HEADERS)
    auth_response = session.post(f"{Credentials.BASE_URL}/auth", json=Credentials.JSON_BODY)
    assert auth_response.status_code == 200, "Ошибка авторизации, статус код не 200"
    token = auth_response.json().get("token")
    assert token is not None, "Токен не найден в ответе"
    session.headers.update({"Cookie": f"token={token}"})
    return session


@pytest.fixture
def api_client(auth_session):
    return ItemApiClient(auth_session)


@pytest.fixture
def item_scenarios(api_client):
    return ItemScenarios(api_client)


##########################################################################################
"""ASYNC"""


@pytest_asyncio.fixture
async def as_auth_session(set_client):
    param = set_client
    if param == "aiohttp":
        connector = aiohttp.TCPConnector(
            ssl=False,
            force_close=True,  # Принудительно закрывать соединения
            enable_cleanup_closed=True  # Очищать закрытые соединения
        )

        # Используем ClientSession с connector
        async with aiohttp.ClientSession(
                headers=Credentials.HEADERS,
                connector=connector,
                trust_env=True  # Доверять переменным окружения
        ) as session:
            async with session.post(
                    f"{Credentials.BASE_URL}/auth",
                    json=Credentials.JSON_BODY
            ) as response:
                data = await response.json()
                token = data["token"]

            # Обновляем заголовки
            session._default_headers.update({"Cookie": f"token={token}"})
            yield session

    elif param == "httpx":
        async with httpx.AsyncClient(
                headers=Credentials.HEADERS,
                verify=False,
                timeout=httpx.Timeout(connect=20.0, read=300.0, write=20.0, pool=20.0),
        ) as session:
            response = await session.post(f"{Credentials.BASE_URL}/auth", json=Credentials.JSON_BODY)
            token = response.json()["token"]
            session.headers.update({"Cookie": f"token={token}"})
            yield session

    else:
        raise ValueError(f"Неизвестный клиент: {param}")


@pytest_asyncio.fixture
async def as_api_client(as_auth_session):
    return AsyncItemApiClient(as_auth_session)


@pytest_asyncio.fixture
async def as_item_scenarios(as_api_client):
    return ItemScenariosAsync(as_api_client)
