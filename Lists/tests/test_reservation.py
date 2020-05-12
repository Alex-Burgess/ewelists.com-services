import pytest
import os
import json
from lists import reservation, logger

log = logger.setup_test_logger()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'RESERVATIONID_INDEX', 'reservationId-index')


class TestReservationMain:
    def test_reservation_main(self, env_vars, api_reservation_event, dynamodb_mock):
        response = reservation.reservation_main(api_reservation_event)
        body = json.loads(response['body'])

        assert body['reservationId'] == "12345678-resv-0001-1234-abcdefghijkl", "Attribute was not correct."
        assert body['userId'] == "12345678-user-0002-1234-abcdefghijkl", "Attribute was not correct."
        assert body['name'] == "Test User2", "Attribute was not correct."
        assert body['email'] == "test.user2@gmail.com", "Attribute was not correct."
        assert body['listId'] == "12345678-list-0001-1234-abcdefghijkl", "Attribute was not correct."
        assert body['listTitle'] == "Child User1 1st Birthday", "Attribute was not correct."
        assert body['productId'] == "12345678-prod-0001-1234-abcdefghijkl", "Attribute was not correct."
        assert body['productType'] == "products", "Attribute was not correct."
        assert body['quantity'] == 1, "Attribute was not correct."
        assert body['state'] == "reserved", "Attribute was not correct."

    def test_reservation_does_not_exist(self, env_vars, api_reservation_event, dynamodb_mock):
        api_reservation_event['pathParameters']['id'] = "12345678-resv-miss-1234-abcdefghijkl"

        response = reservation.reservation_main(api_reservation_event)
        body = json.loads(response['body'])

        assert body['error'] == "Reservation ID does not exist.", "Response did not contain the correct error message."


def test_handler(api_reservation_event, env_vars, dynamodb_mock):
    response = reservation.handler(api_reservation_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert body['reservationId'] == '12345678-resv-0001-1234-abcdefghijkl'
