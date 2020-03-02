import pytest
import os
import json
import boto3
from moto import mock_dynamodb2
from lists import delete_reservation, logger
from tests import fixtures

log = logger.setup_logger()


@pytest.fixture
def api_gateway_event():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/reservation/{id}"
    event['path'] = "/reservation/12345678-resv-0001-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
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


class TestDeleteReservationItem:
    def test_delete_item(self, dynamodb_mock):
        id = '12345678-resv-0001-1234-abcdefghijkl'
        result = delete_reservation.delete_reservation_item('lists-unittest', id)
        assert result, "Reservation was not deleted from table."

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "RESERVATION#" + id}, 'SK': {'S': "RESERVATION#" + id}}
        )

        assert 'Item' not in test_response, "Reservation ID should not exist."

    def test_delete_with_no_table(self, dynamodb_mock):
        id = '12345678-resv-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete_reservation.delete_reservation_item('missing', id)
        assert str(e.value) == "Reservation item could not be deleted.", "Exception not as expected."

    def test_delete_non_existent__item(self, dynamodb_mock):
        id = '12345678-resv-miss-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete_reservation.delete_reservation_item('lists-unittest', id)
        assert str(e.value) == "Reservation item could not be deleted.", "Exception not as expected."


class TestDeleteMain:
    def test_delete_main(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = delete_reservation.delete_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['deleted'], "Attribute was not correct."

    def test_reservation_does_not_exist(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['id'] = "12345678-miss-0001-1234-abcdefghijkl"

        response = delete_reservation.delete_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "Reservation item could not be deleted.", "Error was not correct."

    def test_reservation_id_is_null(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['id'] = "null"

        response = delete_reservation.delete_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "Path contained a null id parameter.", "Error was not correct."


def test_handler(api_gateway_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = delete_reservation.handler(api_gateway_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    assert body['deleted'], "Response body was not as expected."
