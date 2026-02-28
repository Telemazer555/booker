from src.data_models.data_models import BookingResponseData

import pytest
import asyncio


class TestBookingScenarios:

    def test_get_and_verify(self, item_scenarios):
        item_scenarios.get_and_verify_items_exist()

    def test_create_item_and_delete(self, item_scenarios):
        booking_data2 = BookingResponseData()
        for i in range(3):
            item_scenarios.create_item_and_immediately_delete(item_data=booking_data2)

    def test_update_and_get_and_delete(self, item_scenarios):
        booking_data_create = BookingResponseData()
        booking_data_update = BookingResponseData()
        item_scenarios.update_item_and_verify_changes_and_delete(item_data=booking_data_create,
                                                                 upd_item_data=booking_data_update)

    def test_2e(self, api_client):
        booking_data = BookingResponseData()
        uuid = api_client.create_item(item_data=booking_data)
        uuid.json().get("bookingid")
        print(uuid)


class TestBookingScenariosAsync:

    @pytest.mark.asyncio
    async def test_as_get_and_verify_items_exist_aiohttp_httpx(self, as_item_scenarios):
        tasks = [as_item_scenarios.as_get_and_verify_items_exist() for _ in range(5)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_as_create_item_and_delete(self, as_item_scenarios):
        # booking_data_create = BookingResponseData()
        tasks = [as_item_scenarios.as_create_item_and_immediately_delete(item_data=BookingResponseData()) for _ in
                 range(6)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_as_update_and_get_and_delete(self, as_item_scenarios):
        # booking_data_create = BookingResponseData()
        # booking_data_update = BookingResponseData()
        tasks = [as_item_scenarios.as_update_item_and_verify_changes_and_delete(item_data=BookingResponseData(),
                                                                                upd_item_data=BookingResponseData()) for _
                 in range(10)]
        await asyncio.gather(*tasks)
