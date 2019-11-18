import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import add_product
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
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0100-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0100-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"quantity\": 1,\n    \"productType\": \"products\"\n}"

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


class TestCreateProductItem:
    def test_create_product_item(self, dynamodb_mock):
        product_id = '12345678-prod-0010-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        result = add_product.create_product_item('lists-unittest', list_id, product_id, 'products', 1)
        assert result, "Product was not added to table."

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        assert test_response['Item']['PK']['S'] == 'LIST#12345678-list-0001-1234-abcdefghijkl', "List ID not as expected."
        assert test_response['Item']['SK']['S'] == 'PRODUCT#12345678-prod-0010-1234-abcdefghijkl', "Product Id not as expected."
        assert test_response['Item']['type']['S'] == 'products', "Product type not as expected."
        assert test_response['Item']['quantity']['N'] == '1', "Quantity not as expected."
        assert test_response['Item']['reserved']['N'] == '0', "Quantity not as expected."

    def test_with_quantity_2(self, dynamodb_mock):
        product_id = '12345678-prod-0011-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        result = add_product.create_product_item('lists-unittest', list_id, product_id, 'products', 2)
        assert result, "Product was not added to table."

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        assert test_response['Item']['quantity']['N'] == '2', "Quantity not as expected."

    def test_create_product_item_with_no_table(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            add_product.create_product_item('lists-unittes', list_id, product_id, 'products', 1)
        assert str(e.value) == "Product could not be created.", "Exception not as expected."


class TestCreateProductMain:
    def test_create_product_for_products(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = add_product.add_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['message'], "Add product main response did not contain the correct status."

    def test_create_product_with_wrong_type(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"wrong\"\n}'
        response = add_product.add_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "API Event did not contain a product type of products or notfound.", "Error not as expected."

    def test_create_product_with_no_quantity(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['body'] = '{\n    \"productType\": \"products\"\n}'
        response = add_product.add_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "API Event did not contain the quantity in the body.", "Error not as expected."

    def test_create_product_with_not_owner(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"
        response = add_product.add_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No list exists with this ID.", "Error not as expected."

    def test_add_product_with_no_list_id(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['id'] = '12345678-list-0200-1234-abcdefghijkl'
        response = add_product.add_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No list exists with this ID.", "Error not as expected."

    def test_add_product_with_no_product_id(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['productid'] = ''
        response = add_product.add_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "API Event did not contain a Product ID in the path parameters.", "Error not as expected."

    def test_add_product_which_already_exists(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['productid'] = '12345678-prod-0001-1234-abcdefghijkl'
        response = add_product.add_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "Product already exists in list.", "Error not as expected."


def test_handler(api_gateway_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = add_product.handler(api_gateway_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    assert re.match('{"message": .*}', response['body']), "Response body was not as expected."
