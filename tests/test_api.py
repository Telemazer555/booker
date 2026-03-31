from src.data_models.data_models import BookingResponseDataModel

import pytest
import asyncio


class TestBookingScenarios:

    def test_get_and_verify(self, item_scenarios):
        item_scenarios.get_and_verify_items_exist()

    def test_create_item_and_delete(self, item_scenarios, booking_factory):
        item_scenarios.create_validate_item(booking_factory)

    def test_update_and_get_and_delete(self, item_scenarios, booking_factory):
        item_scenarios.update_validate_item(booking_factory)


class TestBookingScenariosAsync:

    @pytest.mark.asyncio
    async def test_as_get_and_verify_items_exist_aiohttp_httpx(self, as_item_scenarios):
        tasks = [as_item_scenarios.as_get_and_verify_items_exist() for _ in range(5)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_as_create_and_get_and_delete(self, as_item_scenarios, booking_factory_async):
        tasks = [as_item_scenarios.as_create_item_and_verify(booking_factory_async) for _ in range(5)]
        await asyncio.gather(*tasks)

    @pytest.mark.asyncio
    async def test_as_update_and_get_and_delete(self, as_item_scenarios, booking_factory_async, ):
        tasks = [
            as_item_scenarios.as_update_item_and_verify(
                booking_factory_async) for _ in range(10)]
        await asyncio.gather(*tasks)