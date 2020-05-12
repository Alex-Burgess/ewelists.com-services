import pytest
import mock
import os
import json
import boto3
from lists import unreserve, logger

log = logger.setup_test_logger()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'EMAIL_INDEX', 'email-index')
    monkeypatch.setitem(os.environ, 'RESERVATIONID_INDEX', 'reservationId-index')

    return monkeypatch


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
class TestUnreserveProduct:
    def test_unreserve_product(self, dynamodb_mock):
        product_key = {}
        reservation_key = {}
        new_product_reserved_quantity = 1
        assert unreserve.unreserve_product('lists-unittest', product_key, reservation_key, new_product_reserved_quantity)

    # TODO - add tests for failure exceptions


class TestUnreserveMain:
    def test_no_reservation_id(self, env_vars, api_unreserve_event):
        api_unreserve_event['pathParameters'] = {"id": "null", "email": "test.user2@gmail.com"}
        response = unreserve.unreserve_main(api_unreserve_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null id parameter.', "Error for missing environment variable was not as expected."

    def test_no_email(self, env_vars, api_unreserve_event):
        api_unreserve_event['pathParameters'] = {"id": "12345678-resv-0002-1234-abcdefghijkl", "email": "null"}
        response = unreserve.unreserve_main(api_unreserve_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null email parameter.', "Error for missing environment variable was not as expected."

    @mock.patch("lists.unreserve.unreserve_product", mock.MagicMock(return_value=[True]))
    def test_unreserve_product_for_user(self, env_vars, dynamodb_mock, api_unreserve_event):
        response = unreserve.unreserve_main(api_unreserve_event)
        body = json.loads(response['body'])
        assert body['unreserved'], "Unreserve main response did not contain the correct status."

    def test_unreserve_product_not_reserved_by_requestor(self, env_vars, dynamodb_mock, api_unreserve_event):
        api_unreserve_event['pathParameters'] = {"id": "12345678-resv-0002-1234-abcdefghijkl", "email": "test.user2@gmail.com"}
        response = unreserve.unreserve_main(api_unreserve_event)
        body = json.loads(response['body'])
        assert body['error'] == "Requestor is not reservation owner.", "Error was not as expected"

    def test_unreserve_product_already_confirmed(self, env_vars, dynamodb_mock, api_unreserve_event):
        api_unreserve_event['pathParameters'] = {"id": "12345678-resv-0006-1234-abcdefghijkl", "email": "test.user2@gmail.com"}
        response = unreserve.unreserve_main(api_unreserve_event)
        body = json.loads(response['body'])
        assert body['error'] == "Product was not reserved. State = purchased.", "Error was not as expected"

    def test_unreserve_product_with_wrong_quantities(self, env_vars, dynamodb_mock, api_unreserve_event):
        # Update table to break concurrency of product reserved quantity, with that of the reserved items.
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')
        dynamodb.update_item(
            TableName='lists-unittest',
            Key={
                'PK': {'S': "LIST#12345678-list-0001-1234-abcdefghijkl"},
                'SK': {'S': "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}
            },
            UpdateExpression="set reserved = :r",
            ExpressionAttributeValues={':r': {'N': str(0)}}
        )

        response = unreserve.unreserve_main(api_unreserve_event)
        body = json.loads(response['body'])
        assert body['error'] == "Reserved quantity for product (0) could not be updated by -1.", "Error was not as expected"


@mock.patch("lists.unreserve.unreserve_product", mock.MagicMock(return_value=[True]))
def test_handler(api_unreserve_event, env_vars, dynamodb_mock):
    response = unreserve.handler(api_unreserve_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['unreserved']


@mock.patch("lists.unreserve.unreserve_product", mock.MagicMock(return_value=[True]))
def test_handler_with_email(api_unreserve_event, env_vars, dynamodb_mock):
    response = unreserve.handler(api_unreserve_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['unreserved']
