import pytest
import mock
import os
import json
from lists import update_reservation, logger

log = logger.setup_test_logger()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'EMAIL_INDEX', 'email-index')
    monkeypatch.setitem(os.environ, 'RESERVATIONID_INDEX', 'reservationId-index')

    return monkeypatch


@pytest.fixture
def reservation_item():
    return {
        'reservationId': '12345678-resv-0001-1234-abcdefghijkl',
        'productId': '12345678-prod-0001-1234-abcdefghijkl',
        'userId': '12345678-user-0002-1234-abcdefghijkl',
        'listId': '12345678-list-0001-1234-abcdefghijkl',
        'name': 'Test User2',
        'email': 'test.user2@gmail.com',
        'quantity': 1,
        'state': 'reserved',
        'listTitle': 'Birthday List',
        'productType': 'products',
    }


class TestCalculateDifferenceToReservedItemQuantity:
    def test_increase_from_1_to_2(self, reservation_item):
        difference = update_reservation.calculate_difference_to_reserved_item_quantity(reservation_item, 2)
        assert difference == 1

    def test_increase_from_1_to_3(self, reservation_item):
        difference = update_reservation.calculate_difference_to_reserved_item_quantity(reservation_item, 3)
        assert difference == 2

    def test_decrease_from_3_to_1(self, reservation_item):
        reservation_item['quantity'] = 3
        difference = update_reservation.calculate_difference_to_reserved_item_quantity(reservation_item, 1)
        assert difference == -2

    def test_decrease_to_0(self, reservation_item):
        with pytest.raises(Exception) as e:
            update_reservation.calculate_difference_to_reserved_item_quantity(reservation_item, 0)
        assert str(e.value) == "Reserved quantity cannot be reduced to 0.", "Exception message not correct."

    def test_keep_at_1(self, reservation_item):
        with pytest.raises(Exception) as e:
            update_reservation.calculate_difference_to_reserved_item_quantity(reservation_item, 1)
        assert str(e.value) == "There was no difference in update request to reserved item.", "Exception message not correct."


class TestUpdateReserveMain:
    @mock.patch("lists.update_reservation.update_product_and_reservation", mock.MagicMock(return_value=[True]))
    def test_update_reserve_main(self, env_vars, dynamodb_mock, api_update_reservation_event):
        response = update_reservation.update_reserve_main(api_update_reservation_event)
        body = json.loads(response['body'])
        assert body['updated'], "Update reserve main response did not contain the correct status."

    def test_no_reservation_id(self, env_vars, dynamodb_mock, api_update_reservation_event):
        api_update_reservation_event['pathParameters'] = {"id": "12345678-resv-0099-1234-abcdefghijkl", "email": "test.user2@gmail.com"}
        response = update_reservation.update_reserve_main(api_update_reservation_event)
        body = json.loads(response['body'])
        assert body['error'] == "Reservation ID does not exist.", "Error was not as expected"

    def test_update_product_not_reserved(self, env_vars, dynamodb_mock, api_update_reservation_event):
        api_update_reservation_event['pathParameters'] = {"id": "12345678-resv-0006-1234-abcdefghijkl", "email": "test.user2@gmail.com"}
        response = update_reservation.update_reserve_main(api_update_reservation_event)
        body = json.loads(response['body'])
        assert body['error'] == "Product was not reserved. State = purchased.", "Error was not as expected"

    def test_update_product_not_reserved_by_requestor(self, env_vars, dynamodb_mock, api_update_reservation_event):
        api_update_reservation_event['pathParameters'] = {"id": "12345678-resv-0001-1234-abcdefghijkl", "email": "test.user1@gmail.com"}
        response = update_reservation.update_reserve_main(api_update_reservation_event)
        body = json.loads(response['body'])
        assert body['error'] == "Requestor is not reservation owner.", "Error was not as expected"

    def test_update_reserved_quantity_to_zero(self, env_vars, dynamodb_mock, api_update_reservation_event):
        api_update_reservation_event['body'] = "{\n    \"quantity\": -2\n}"

        response = update_reservation.update_reserve_main(api_update_reservation_event)
        body = json.loads(response['body'])
        assert body['error'] == "Reserved quantity cannot be reduced to 0.", "Error was not as expected"

    def test_update_reserved_quantity_by_too_many(self, env_vars, dynamodb_mock, api_update_reservation_event):
        api_update_reservation_event['body'] = "{\n    \"quantity\": 10\n}"

        response = update_reservation.update_reserve_main(api_update_reservation_event)
        body = json.loads(response['body'])
        assert body['error'] == "Reserved quantity for product (2) could not be updated by 9 as exceeds required quantity (3).", "Error was not as expected"


@mock.patch("lists.update_reservation.update_product_and_reservation", mock.MagicMock(return_value=[True]))
def test_handler_with_email(env_vars, api_update_reservation_event, dynamodb_mock):
    response = update_reservation.handler(api_update_reservation_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['updated']
