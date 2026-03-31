from idlelib.rpc import response_queue

from src.api_manager.api_manager import ItemApiClient, AsyncItemApiClient
from src.data_models.data_models import CreateUserSchemaDataModel, BaseBookingSchemaDataModel, \
    validate_response, validate_response_as, BookingResponseDataModel


class ItemScenarios:
    def __init__(self, api_client: ItemApiClient):  # Типизация для ясности
        self.api_client = api_client

    def get_and_verify_items_exist(self):
        """
        Сценарий: получить список items и проверить, что он не пуст.
        """
        items = self.api_client.get_items().json()
        assert len(items) > 0, "Список items пуст"
        print(f"\nПолучено {len(items)} items.")
        return items

    def create_validate_item(self, booking_factory):
        # Генерируем рандомные данные для отправки
        test_booking_data = BookingResponseDataModel()
        # Отправляем запрос
        response = booking_factory(test_booking_data)
        # Получаем bookingid из ответа
        response_data = response.json()
        booking_id = response_data.get("bookingid")
        # Формируем ожидаемые данные для проверки
        expected_full_data = {
            "bookingid": booking_id,
            "booking": test_booking_data.model_dump()
        }
        # Проверяем ответ
        validate_response(response, model=CreateUserSchemaDataModel, expected_data=expected_full_data)
        return booking_id

    def update_validate_item(self, booking_factory):
        # Генерируем рандомные данные для отправки
        created_booking_data = BookingResponseDataModel()
        # Отправляем запрос
        created_item_data = booking_factory(created_booking_data)
        # Формируем ожидаемые данные для проверки
        uuid = created_item_data.json()['bookingid']
        firstname = created_item_data.json()['booking']['firstname']
        lastname = created_item_data.json()['booking']['lastname']
        expected_full_data = {
            "bookingid": uuid,
            "booking": created_booking_data.model_dump()
        }
        # Проверяем ответ
        validate_response(created_item_data, model=CreateUserSchemaDataModel, expected_data=expected_full_data)
        # Создаём обновляемые данные
        update_booking_data = BookingResponseDataModel()
        # Обновляем запрос
        response_queueup_booking_data = self.api_client.update_item(uuid, update_booking_data)
        # Формируем ожидаемые данные для проверки
        up_firstname = response_queueup_booking_data.json()['firstname']
        up_lastname = response_queueup_booking_data.json()['lastname']
        update_expected_full_data = update_booking_data.model_dump()
        # Проверяем ответ
        validate_response(response_queueup_booking_data, model=BaseBookingSchemaDataModel,
                          expected_data=update_expected_full_data)

        assert up_firstname != firstname, "Имя  совпадает"
        assert up_lastname != lastname, "Фамилия  совпадает"


class ItemScenariosAsync:

    def __init__(self, api_client: AsyncItemApiClient):
        self.api_client = api_client

    async def as_get_and_verify_items_exist(self):
        response = await self.api_client.as_get_items()
        js_item = await self.api_client.extract_response(response)
        assert len(js_item) > 0, "Список items пуст"
        print(f"\nПолучено {len(js_item)} items.")
        return js_item


    async def as_create_item_and_verify(self, booking_factory_async):
        # Генерируем тестовые данные
        test_booking_data = BookingResponseDataModel()
        # Отправляем запрос
        response = await booking_factory_async(test_booking_data)
        # Если response уже dict
        booking_id = response["bookingid"]
        # Формируем ожидаемые данные
        expected_full_data = {
            "bookingid": booking_id,
            "booking": test_booking_data.model_dump()
        }
        # Проверяем ответ
        await validate_response_as(
            response,
            model=CreateUserSchemaDataModel,
            expected_data=expected_full_data
        )
        return booking_id

    async def as_update_item_and_verify(self, booking_factory_async):
        # Создаём исходное бронирование
        created_booking_data = BookingResponseDataModel()
        created_item_data = await booking_factory_async(created_booking_data)
        # Достаём данные из create response
        booking_id = created_item_data["bookingid"]
        firstname = created_item_data["booking"]["firstname"]
        lastname = created_item_data["booking"]["lastname"]
        # Формируем expected для create
        expected_create_data = {
            "bookingid": booking_id,
            "booking": created_booking_data.model_dump()
        }
        # Валидируем create response
        await validate_response_as(
            created_item_data,
            model=CreateUserSchemaDataModel,
            expected_data=expected_create_data
        )

        # Генерируем новые данные для update
        update_booking_data = BookingResponseDataModel()
        # Отправляем update запрос
        update_response = await self.api_client.as_update_item(booking_id, update_booking_data)
        # Превращаем response в dict
        updated_data = await self.api_client.extract_response(update_response)
        # Достаём новые значения
        up_firstname = updated_data["firstname"]
        up_lastname = updated_data["lastname"]
        # Формируем expected для update
        update_expected_full_data = update_booking_data.model_dump()
        # Валидируем update response
        await validate_response_as(
            updated_data,
            model=BaseBookingSchemaDataModel,
            expected_data=update_expected_full_data
        )
        # Проверяем, что данные реально изменились
        assert up_firstname != firstname, "Имя совпадает"
        assert up_lastname != lastname, "Фамилия совпадает"

        return booking_id