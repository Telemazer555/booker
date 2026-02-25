from src.api_manager.api_manager import ItemApiClient, Validator, AsyncItemApiClient
from src.data_models.data_models import UserSchema2, UpdateBookingSchema, Credentials


class ItemScenarios:
    def __init__(self, api_client: ItemApiClient):  # Типизация для ясности
        self.api_client = api_client
        self.validator = Validator()

    def create_item_and_immediately_delete(self, item_data):
        """
        Сценарий: создать item, проверить его ответ через валидатор и сразу же его удалить.
        Возвращает ID созданного и удаленного item.
        """
        created_item_data = self.api_client.create_item(item_data)
        self.validator.validate_response(created_item_data, expected_data=created_item_data.json(), model=UserSchema2)

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

        self.validator.validate_response(create_booking, expected_data=create_booking.json(), model=UserSchema2)
        uuid = create_booking.json()['bookingid']
        firstname = create_booking.json()['booking']['firstname']
        lastname = create_booking.json()['booking']['lastname']

        up_booking_data = self.api_client.update_item(uuid, upd_item_data)

        self.validator.validate_response(up_booking_data, expected_data=up_booking_data.json(),
                                         model=UpdateBookingSchema)

        up_firstname = up_booking_data.json()['firstname']
        up_lastname = up_booking_data.json()['lastname']

        assert up_firstname != firstname, "Имя  совпадает"
        assert up_lastname != lastname, "Фамилия  совпадает"

        print(f"\nУспешно удалён item с ID:{uuid} и стаскодом {self.api_client.delete_item(uuid).status_code}")


class ItemScenariosAsync:
    def __init__(self, api_client: AsyncItemApiClient):
        self.api_client = api_client
        self.validator = Validator()

    async def as_get_and_verify_items_exist(self):
        response = await self.api_client.as_get_items()
        items =  response.json()
        assert len(items) > 0, "Список items пуст"
        print(f"\nПолучено {len(items)} items.")
        return items

    async def as_get_and_verify_items_exist_aiohttp(self):
        response = await self.api_client.as_get_items_aiohttp()
        items = await response.json()
        assert len(items) > 0, "Список items пуст"
        print(f"\nПолучено {len(items)} items.")
        return items

    async def as_get_and_verify_items_exist_aiohttp2(self):
        response = await self.api_client.as_get_items_aiohttp2()
        if Credentials.AS_CLIENT == "aiohttp":
            items = await response.json()
        elif Credentials.AS_CLIENT == "httpx":
            items = response.json()
        assert len(items) > 0, "Список items пуст"
        print(f"\nПолучено {len(items)} items.")
        return items

    async def as_create_item_and_immediately_delete(self, item_data):
        responses = await self.api_client.as_create_item(item_data)
        self.validator.validate_response(responses, expected_data=responses.json(), model=UserSchema2)
        id_booking = responses.json().get("bookingid")
        await self.api_client.as_get_item(id_booking)
        print(
            f"\n ID {id_booking} успешно создан.\n ID {id_booking} Успешно удалён. статус код: {await self.api_client.as_delete_item(id_booking)}.")
        return id_booking

    async def as_update_item_and_verify_changes_and_delete(self, item_data, upd_item_data):
        create_booking = await self.api_client.as_create_item(item_data)
        self.validator.validate_response(create_booking, expected_data=create_booking.json(), model=UserSchema2)
        uuid = create_booking.json()['bookingid']
        firstname = create_booking.json()['booking']['firstname']
        lastname = create_booking.json()['booking']['lastname']

        update = await self.api_client.as_update_item(uuid, upd_item_data)
        self.validator.validate_response(update, expected_data=update.json(), model=UpdateBookingSchema)

        up_firstname = update.json()['firstname']
        up_lastname = update.json()['lastname']

        assert firstname != up_firstname, "Имя  совпадает"
        assert lastname != up_lastname, "Фамилия  совпадает"

        print(f"\nУспешно удалён item с ID:{uuid} и стаскодом {await self.api_client.as_delete_item(uuid)}")
