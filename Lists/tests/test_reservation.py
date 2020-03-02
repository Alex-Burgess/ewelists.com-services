import pytest
import os
import json
import boto3
from moto import mock_dynamodb2
from lists import reservation, logger
from tests import fixtures

log = logger.setup_logger()


@pytest.fixture
def api_gateway_event():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/reservation/{id}"
    event['path'] = "/reservation/12345678-resv-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-resv-0001-1234-abcdefghijkl"}

    return event


@pytest.fixture
def dynamodb_mock():
    mock = mock_dynamodb2()
    mock.start()
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = dynamodb.create_table(
        TableName='lists-unittest',
        KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}, {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{'AttributeName': 'PK', 'AttributeType': 'S'}, {'AttributeName': 'SK', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    items = fixtures.load_test_data()

    for item in items:
        table.put_item(TableName='lists-unittest', Item=item)

    yield
    mock.stop()


class TestGetReservation:
    def test_get_reservation(self, dynamodb_mock):
        resv_id = "12345678-resv-0001-1234-abcdefghijkl"
        item = reservation.get_reservation('lists-unittest', resv_id)

        expected_item = {
            'PK': {'S': 'RESERVATION#12345678-resv-0001-1234-abcdefghijkl'},
            'SK': {'S': 'RESERVATION#12345678-resv-0001-1234-abcdefghijkl'},
            'reservationId': {'S': '12345678-resv-0001-1234-abcdefghijkl'},
            'userId': {'S': '12345678-user-0002-1234-abcdefghijkl'},
            'name': {'S': 'Test User2'},
            'email': {'S': 'test.user2@gmail.com'},
            'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'},
            'title': {'S': 'Child User1 1st Birthday'},
            'productId': {'S': '12345678-prod-0001-1234-abcdefghijkl'},
            'productType': {'S': 'products'},
            'quantity': {'N': '1'},
            'state': {'S': 'reserved'}
        }

        assert item == expected_item, "Item returned was not as expected."

    def test_get_reservation_with_wrong_table(self, dynamodb_mock):
        resv_id = "12345678-resv-0001-1234-abcdefghijkl"

        with pytest.raises(Exception) as e:
            reservation.get_reservation('wrong-table', resv_id)
        assert str(e.value) == "Unexpected error when getting reservation item from table.", "Exception not as expected."

    def test_with_reservation_id_that_does_not_exist(self, dynamodb_mock):
        resv_id = "12345678-resv-miss-1234-abcdefghijkl"

        with pytest.raises(Exception) as e:
            reservation.get_reservation('lists-unittest', resv_id)
        assert str(e.value) == "Reservation ID 12345678-resv-miss-1234-abcdefghijkl did not exist.", "Exception not as expected."


class TestReservationMain:
    def test_reservation_main(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = reservation.reservation_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['reservationId'] == "12345678-resv-0001-1234-abcdefghijkl", "Attribute was not correct."
        assert body['userId'] == "12345678-user-0002-1234-abcdefghijkl", "Attribute was not correct."
        assert body['name'] == "Test User2", "Attribute was not correct."
        assert body['email'] == "test.user2@gmail.com", "Attribute was not correct."
        assert body['listId'] == "12345678-list-0001-1234-abcdefghijkl", "Attribute was not correct."
        assert body['title'] == "Child User1 1st Birthday", "Attribute was not correct."
        assert body['productId'] == "12345678-prod-0001-1234-abcdefghijkl", "Attribute was not correct."
        assert body['productType'] == "products", "Attribute was not correct."
        assert body['quantity'] == 1, "Attribute was not correct."
        assert body['state'] == "reserved", "Attribute was not correct."

    def test_reservation_does_not_exist(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['id'] = "12345678-resv-miss-1234-abcdefghijkl"

        response = reservation.reservation_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['error'] == "Reservation ID 12345678-resv-miss-1234-abcdefghijkl did not exist.", "Response did not contain the correct error message."


def test_handler(api_gateway_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = reservation.handler(api_gateway_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert body['reservationId'] == '12345678-resv-0001-1234-abcdefghijkl'
