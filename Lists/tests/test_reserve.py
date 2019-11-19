import pytest
import os
import json
import boto3
from moto import mock_dynamodb2
from lists import reserve
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_event_prod1():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"quantity\": 2,\n    \"message\": \"Happy birthday to you!\"\n}"

    return event


@pytest.fixture
def api_gateway_event_prod2():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0002-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0002-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"quantity\": 1,\n    \"message\": \"Happy birthday to you!\"\n}"

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


class TestGetUsersName:
    def test_get_users_name(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        name = reserve.get_users_name('lists-unittest', user_id)
        assert name == "Test User1", "User's name was not as expected."

    def test_with_invalid_userid(self, dynamodb_mock):
        user_id = '12345678-user-0010-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            reserve.get_users_name('lists-unittest', user_id)
        assert str(e.value) == "No user exists with this ID.", "Exception not as expected."


class TestGetProductQuantities:
    def test_get_product_quantities(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        quantities = reserve.get_product_quantities('lists-unittest', list_id, product_id)

        expected_result = {'quantity': 3, 'reserved': 1}
        assert quantities == expected_result, "Quantities not as expected."

    def test_with_invalid_productid(self, dynamodb_mock):
        product_id = '12345678-prod-0010-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            reserve.get_product_quantities('lists-unittest', list_id, product_id)
        assert str(e.value) == "No product exists with this ID.", "Exception not as expected."


class TestUpdateReservedQuantities:
    def test_with_no_update(self):
        quantities = {'quantity': 1, 'reserved': 0}
        new_reserve_total = reserve.update_reserved_quantities(quantities, 0)
        assert new_reserve_total == 0

    def test_reserve_one_product(self):
        quantities = {'quantity': 1, 'reserved': 0}
        new_reserve_total = reserve.update_reserved_quantities(quantities, 1)
        assert new_reserve_total == 1

    def test_reserve_two_product(self):
        quantities = {'quantity': 2, 'reserved': 0}
        new_reserve_total = reserve.update_reserved_quantities(quantities, 2)
        assert new_reserve_total == 2

    def test_over_reserve(self):
        quantities = {'quantity': 1, 'reserved': 1}
        with pytest.raises(Exception) as e:
            reserve.update_reserved_quantities(quantities, 1)
        assert str(e.value) == "Reserved product quantity 2 exceeds quantity required 1."

    def test_over_reserve2(self):
        quantities = {'quantity': 1, 'reserved': 0}
        with pytest.raises(Exception) as e:
            reserve.update_reserved_quantities(quantities, 2)
        assert str(e.value) == "Reserved product quantity 2 exceeds quantity required 1."


class TestAddReservedDetails:
    def test_reserve_a_product(self, dynamodb_mock):
        table_name = 'lists-unittest'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0002-1234-abcdefghijkl'
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        users_name = 'Test User1'
        request_reserve = 1
        message = 'A test message'
        assert reserve.add_reserved_details(table_name, list_id, product_id, user_id, users_name, request_reserve, message)

        # Check the table was updated with right reserved details
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "RESERVED#PRODUCT#" + product_id}}
        )

        assert test_response['Item']['PK']['S'] == 'LIST#12345678-list-0001-1234-abcdefghijkl', "PK not as expected."
        assert test_response['Item']['SK']['S'] == 'RESERVED#PRODUCT#12345678-prod-0002-1234-abcdefghijkl', "SK not as expected."
        assert test_response['Item']['name']['S'] == 'Test User1', "Users name not as expected."
        assert test_response['Item']['userId']['S'] == '12345678-user-0001-1234-abcdefghijkl', "UserId not as expected."
        assert test_response['Item']['quantity']['N'] == '1', "Quantity not as expected."
        assert test_response['Item']['message']['S'] == 'A test message', "Message not as expected."


class TestUpdateProductReservedQuantity:
    def test_update_quantity(self, dynamodb_mock):
        table_name = 'lists-unittest'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0002-1234-abcdefghijkl'

        assert reserve.update_product_reserved_quantity(table_name, list_id, product_id, 2)


class TestReserveMain:
    def test_reserve_product_not_yet_reserved(self, monkeypatch, api_gateway_event_prod2, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = reserve.reserve_main(api_gateway_event_prod2)
        body = json.loads(response['body'])
        assert body['reserved'], "Reserve response was not true."

        # Check the table was updated with right reserved details
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')
        list_id = api_gateway_event_prod2['pathParameters']['id']
        product_id = api_gateway_event_prod2['pathParameters']['productid']

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        reserved_quantity = int(test_response['Item']['reserved']['N'])
        assert reserved_quantity == 1, "Quantity not as expected."

        reserved_details_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "RESERVED#PRODUCT#" + product_id}}
        )

        assert reserved_details_response['Item']['PK']['S'] == 'LIST#12345678-list-0001-1234-abcdefghijkl', "PK not as expected."
        assert reserved_details_response['Item']['SK']['S'] == 'RESERVED#PRODUCT#12345678-prod-0002-1234-abcdefghijkl', "SK not as expected."
        assert reserved_details_response['Item']['quantity']['N'] == '1', "Quantity not as expected."

    def test_reserve_product_with_one_reserved(self, monkeypatch, api_gateway_event_prod1, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = reserve.reserve_main(api_gateway_event_prod1)
        body = json.loads(response['body'])
        assert body['reserved'], "Reserve response was not true."

        # Check the table was updated with right reserved details
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')
        list_id = api_gateway_event_prod1['pathParameters']['id']
        product_id = api_gateway_event_prod1['pathParameters']['productid']

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        reserved_quantity = int(test_response['Item']['reserved']['N'])
        assert reserved_quantity == 3, "Quantity not as expected."

        reserved_details_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "RESERVED#PRODUCT#" + product_id}}
        )

        assert reserved_details_response['Item']['PK']['S'] == 'LIST#12345678-list-0001-1234-abcdefghijkl', "PK not as expected."
        assert reserved_details_response['Item']['SK']['S'] == 'RESERVED#PRODUCT#12345678-prod-0001-1234-abcdefghijkl', "SK not as expected."
        assert reserved_details_response['Item']['quantity']['N'] == '2', "Quantity not as expected."

    def test_over_reserve_product(self, monkeypatch, api_gateway_event_prod1, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        api_gateway_event_prod1['body'] = "{\n    \"quantity\": 4,\n    \"message\": \"Happy birthday to you!\"\n}"

        response = reserve.reserve_main(api_gateway_event_prod1)
        body = json.loads(response['body'])
        assert body['error'] == 'Reserved product quantity 5 exceeds quantity required 3.', "Reserve error was not as expected."


def test_handler(api_gateway_event_prod1, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = reserve.handler(api_gateway_event_prod1, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['reserved']
