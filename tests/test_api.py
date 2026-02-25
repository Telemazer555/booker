from src.data_models.data_models import BookingResponseData,Clients

import pytest
import asyncio


class TestBookingScenarios:

    @pytest.mark.parametrize("auth_session",[Clients.REQUESTS.value,Clients.HTTPX.value], indirect=True)
    def test_get_and_verify(self, item_scenarios, auth_session):
        item_scenarios.get_and_verify_items_exist()

    @pytest.mark.parametrize("auth_session", [Clients.REQUESTS.value, Clients.HTTPX.value], indirect=True)
    def test_create_item_and_delete(self, item_scenarios, auth_session):
        booking_data2 = BookingResponseData()
        for i in range(1):
            item_scenarios.create_item_and_immediately_delete(item_data=booking_data2)

    @pytest.mark.parametrize("auth_session", [Clients.REQUESTS.value, Clients.HTTPX.value], indirect=True)
    def test_update_and_get_and_delete(self, item_scenarios, auth_session):
        booking_data_create = BookingResponseData()
        booking_data_update = BookingResponseData()
        item_scenarios.update_item_and_verify_changes_and_delete(item_data=booking_data_create,
                                                                 upd_item_data=booking_data_update)

    @pytest.mark.parametrize("auth_session", [Clients.REQUESTS.value, Clients.HTTPX.value], indirect=True)
    def test_2e(self, api_client, auth_session):
        booking_data = BookingResponseData()
        uuid = api_client.create_item(item_data=booking_data)
        uuid.json().get("bookingid")
        print(uuid)


class TestBookingScenariosAsync:

    @pytest.mark.asyncio
    async def test_as_get_and_verify_items_exist(self, as_item_scenarios):
        tasks = [as_item_scenarios.as_get_and_verify_items_exist() for _ in range(5)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_as_get_and_verify_items_exist_aiohttp(self, as_item_scenarios):
        tasks = [as_item_scenarios.as_get_and_verify_items_exist_aiohttp2() for _ in range(5)]
        await asyncio.gather(*tasks)

    @pytest.mark.parametrize("auth_session", [Clients.ASYNC_AIOHTTP.value, Clients.ASYNC_HTTPX.value], indirect=True)
    @pytest.mark.asyncio
    async def test_as_get_and_verify_items_exist_aiohttp3(self, as_item_scenarios, auth_session):
        tasks = [as_item_scenarios.as_get_and_verify_items_exist_aiohttp2() for _ in range(5)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_as_create_item_and_delete(self, as_item_scenarios):
        booking_data_create = BookingResponseData()
        tasks = [as_item_scenarios.as_create_item_and_immediately_delete(item_data=booking_data_create) for _ in range(6)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_as_update_and_get_and_delete(self, as_item_scenarios):
        booking_data_create = BookingResponseData()
        booking_data_update = BookingResponseData()
        tasks = [as_item_scenarios.as_update_item_and_verify_changes_and_delete(item_data=booking_data_create,
                                                                                upd_item_data=booking_data_update) for _
                 in range(10)]
        await asyncio.gather(*tasks)

