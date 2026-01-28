import pytest
import requests

from src.api_manager.api_manager import ItemApiClient
from src.data_models.data_models import Credentials
from src.scenarios.scenarios import ItemScenarios


@pytest.fixture(scope='session')
def auth_session():
    session = requests.session()
    session.headers.update(Credentials.HEADERS)
    session.verify = False
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
