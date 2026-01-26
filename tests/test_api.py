from data_models.data_models import BookingResponseData
# print()
class TestBookingScenarios:

    def test_get_and_verify(self, item_scenarios, booking_data):
        item_scenarios.get_and_verify_items_exist()

    def test_create_item_and_delete(self, item_scenarios, booking_data):
        item_scenarios.create_item_and_immediately_delete(item_data=booking_data)

    def test_create_item_and_delete2(self, item_scenarios ):
        booking_data2 = BookingResponseData()
        item_scenarios.create_item_and_immediately_delete2(item_data=booking_data2)

    def test_update_and_get_and_delete(self, item_scenarios, booking_data,
                                       booking_data_hard):
        item_scenarios.update_item_and_verify_changes_and_delete(item_data=booking_data,
                                                                 upd_item_data=booking_data_hard)
