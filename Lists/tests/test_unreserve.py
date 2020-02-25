import pytest
import os
import json
import boto3
from moto import mock_dynamodb2
from lists import unreserve
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"

    return event


@pytest.fixture
def api_gateway_event_with_email():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}/email/{email}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/test.user99@gmail.com"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
    event['body'] = "{\n    \"name\": \"Test User99\"\n}"

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
    # teardown: stop moto server
    mock.stop()


class TestUnreserveMain:
    @pytest.mark.skip(reason="transact_write_items is not implemented for moto")
    def test_unreserve_product_for_user(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unreserve.unreserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['unreserved'], "Unreserve main response did not contain the correct status."

    def test_unreserve_product_not_reserved(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters'] = {"productid": "12345678-prod-0011-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
        response = unreserve.unreserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No reserved item exists with this ID.", "Error was not as expected"

    def test_unreserve_product_not_added_to_list(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0011-1234-abcdefghijkl"}
        response = unreserve.unreserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No reserved item exists with this ID.", "Error was not as expected"

    def test_unreserve_product_not_reserved_by_requestor(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0001-1234-abcdefghijkl"
        response = unreserve.unreserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No reserved item exists with this ID.", "Error was not as expected"

    def test_unreserve_product_with_wrong_quantities(self, monkeypatch, dynamodb_mock, api_gateway_event):
        # Update table to break concurrency of product reserved quantity, with that of the reserved items.
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')
        key = {
            'PK': {'S': "LIST#{}".format(api_gateway_event['pathParameters']['id'])},
            'SK': {'S': "PRODUCT#{}".format(api_gateway_event['pathParameters']['productid'])}
        }

        response = dynamodb.update_item(
            TableName='lists-unittest',
            Key=key,
            UpdateExpression="set reserved = :r",
            ExpressionAttributeValues={
                ':r': {'N': str(0)},
            }
        )

        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unreserve.unreserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "Reserved quantity for product (0) could not be updated by -1.", "Error was not as expected"


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
def test_handler(api_gateway_event_prod1, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = unreserve.handler(api_gateway_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['reserved']


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
def test_handler_with_email(api_gateway_event_with_email, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = unreserve.handler(api_gateway_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['reserved']
