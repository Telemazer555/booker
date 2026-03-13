from src.api_manager.api_manager import ItemApiClient, AsyncItemApiClient
# from src.data_models.data_models import CreateUserSchema, Validator, BaseBookingSchema, Credentials
from src.data_models.data_models import CreateUserSchemaDataModel, BaseBookingSchemaDataModel, Credentials, validate_response, \
    validate_response_aiohttp
from functools import wraps


class ItemScenarios:
    def __init__(self, api_client: ItemApiClient):  # Типизация для ясности
        self.api_client = api_client
        # self.validator = Validator()

    def create_item_and_immediately_delete(self, item_data):
        """
        Сценарий: создать item, проверить его ответ через валидатор и сразу же его удалить.
        Возвращает ID созданного и удаленного item.
        """
        created_item_data = self.api_client.create_item(item_data)
        validate_response(response=created_item_data, model=CreateUserSchemaDataModel)

        item_id = created_item_data.json().get("bookingid")
        self.api_client.get_item(item_id)
        print(
            f"\n ID {item_id} успешно создан.\n ID {item_id} Успешно удалён. статус код: {self.api_client.delete_item(item_id).status_code}.")
        return item_id

    def get_and_verify_items_exist(self):
        """
        Сценарий: получить список items и проверить, что он не пуст.
        """
        items = self.api_client.get_items().json()
        assert len(items) > 0, "Список items пуст"
        print(f"\nПолучено {len(items)} items.")
        return items

    def update_item_and_verify_changes_and_delete(self, item_data, upd_item_data):
        create_booking = self.api_client.create_item(item_data)

        validate_response(create_booking, model=CreateUserSchemaDataModel)
        uuid = create_booking.json()['bookingid']
        firstname = create_booking.json()['booking']['firstname']
        lastname = create_booking.json()['booking']['lastname']

        up_booking_data = self.api_client.update_item(uuid, upd_item_data)

        validate_response(up_booking_data, expected_data=up_booking_data.json(),
                          model=BaseBookingSchemaDataModel)

        up_firstname = up_booking_data.json()['firstname']
        up_lastname = up_booking_data.json()['lastname']

        assert up_firstname != firstname, "Имя  совпадает"
        assert up_lastname != lastname, "Фамилия  совпадает"

        print(f"\nУспешно удалён item с ID:{uuid} и стаскодом {self.api_client.delete_item(uuid).status_code}")


def choice_client(func):
    @wraps(func)
    async def async_client_wrapper(*agrs, **kwargs):
        response = await func(*agrs, **kwargs)

        if Credentials.CLIENT == "aiohttp":
            items = await response.json()

        elif Credentials.CLIENT == "httpx":
            items = response.json()

        return items

    return async_client_wrapper


class ItemScenariosAsync:

    def __init__(self, api_client: AsyncItemApiClient):
        self.api_client = api_client
        # self.validator = Validator()

    # async def as_get_and_verify_items_exist(self):
    #     response = await self.api_client.as_get_items()
    #
    #     if Credentials.CLIENT == "aiohttp":
    #         items = await response.json()
    #
    #     elif Credentials.CLIENT == "httpx":
    #         items = response.json()
    #
    #     assert len(items) > 0, "Список items пуст"
    #     print(f"\nПолучено {len(items)} items.")
    #     return items

    async def as_get_and_verify_items_exist(self):
        response = await self.api_client.as_get_items()

        if Credentials.CLIENT == "aiohttp":
            items = await response.json()

        elif Credentials.CLIENT == "httpx":
            items = response.json()

        assert len(items) > 0, "Список items пуст"
        print(f"\nПолучено {len(items)} items.")
        return items

    async def as_create_item_and_immediately_delete(self, item_data):

        responses = await self.api_client.as_create_item(item_data)

        if Credentials.CLIENT == "aiohttp":
            response_data = await responses.json()
            id_booking = response_data.get("bookingid")
            await validate_response_aiohttp(responses, expected_data=response_data,
                                            model=CreateUserSchemaDataModel)
        elif Credentials.CLIENT == "httpx":
            response_data = responses.json()
            id_booking = response_data.get("bookingid")
            validate_response(responses, expected_data=response_data, model=CreateUserSchemaDataModel)

        # Получаем и удаляем item
        await self.api_client.as_get_item(id_booking)
        delete_status = await self.api_client.as_delete_item(id_booking)
        print(f"\nID {id_booking} успешно создан.\nID {id_booking} успешно удалён. Статус код: {delete_status}.")
        return id_booking

    async def as_update_item_and_verify_changes_and_delete(self, item_data, upd_item_data):
        # Создание бронирования
        create_booking = await self.api_client.as_create_item(item_data)
        if Credentials.CLIENT == "aiohttp":
            create_response_data = await create_booking.json()
            await validate_response_aiohttp(create_booking, expected_data=create_response_data,
                                            model=CreateUserSchemaDataModel)
            uuid = create_response_data['bookingid']
            firstname = create_response_data['booking']['firstname']
            lastname = create_response_data['booking']['lastname']
        elif Credentials.CLIENT == "httpx":
            create_response_data = create_booking.json()
            validate_response(create_booking, expected_data=create_response_data, model=CreateUserSchemaDataModel)
            uuid = create_response_data['bookingid']
            firstname = create_response_data['booking']['firstname']
            lastname = create_response_data['booking']['lastname']

        # Обновление бронирования
        update_response = await self.api_client.as_update_item(uuid, upd_item_data)
        if Credentials.CLIENT == "aiohttp":
            update_response_data = await update_response.json()
            await validate_response_aiohttp(update_response, expected_data=update_response_data,
                                            model=BaseBookingSchemaDataModel)
            up_firstname = update_response_data['firstname']
            up_lastname = update_response_data['lastname']
        elif Credentials.CLIENT == "httpx":
            update_response_data = update_response.json()
            validate_response(update_response, expected_data=update_response_data,
                              model=BaseBookingSchemaDataModel)
            up_firstname = update_response_data['firstname']
            up_lastname = update_response_data['lastname']

        assert firstname != up_firstname, "Имя не изменилось"
        assert lastname != up_lastname, "Фамилия не изменилась"

        delete_status = await self.api_client.as_delete_item(uuid)
        print(f"\nУспешно удалён item с ID:{uuid} и статус кодом {delete_status}")
