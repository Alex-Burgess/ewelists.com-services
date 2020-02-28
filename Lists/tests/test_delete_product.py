import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import delete_product
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
    event['resource'] = "/lists/{id}/product/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"productType\": \"products\"\n}"

    return event


@pytest.fixture
def dynamodb_mock():
    table_name = 'lists-unittest'

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
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestDeleteProductItem:
    def test_delete_product_item(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        result = delete_product.delete_product_item('lists-unittest', list_id, product_id)
        assert result, "Product was not deleted from table."

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        assert 'Item' not in test_response, "Product ID should not exist."

    def test_delete_product_item_with_no_table(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete_product.delete_product_item('lists-unittes', list_id, product_id)
        assert str(e.value) == "Product could not be deleted.", "Exception not as expected."

    def test_delete_non_existent_product_item(self, dynamodb_mock):
        product_id = '112345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete_product.delete_product_item('lists-unittest', list_id, product_id)
        assert str(e.value) == "Product could not be deleted.", "Exception not as expected."


class TestDeleteProductMain:
    def test_delete_product(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = delete_product.delete_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['message'], "Delete product main response did not contain the correct status."

    def test_delete_product_with_not_owner(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"
        response = delete_product.delete_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No list exists with this ID.", "Error not as expected."

    def test_delete_product_with_no_list_id(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['id'] = '12345678-list-0200-1234-abcdefghijkl'
        response = delete_product.delete_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No list exists with this ID.", "Error not as expected."

    def test_delete_product_with_no_product_id(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['productid'] = "null"
        response = delete_product.delete_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "Path contained a null productid parameter.", "Error not as expected."


def test_handler(api_gateway_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = delete_product.handler(api_gateway_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    assert re.match('{"message": .*}', response['body']), "Response body was not as expected."
