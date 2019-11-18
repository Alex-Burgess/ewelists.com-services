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
def api_gateway_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
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

    # 1 User, with 1 list.
    items = [
        {"PK": "USER#12345678-user-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "email": "test.user@gmail.com", "name": "Test User", "userId": "12345678-user-0001-1234-abcdefghijkl"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl", "type": "products", "quantity": 1, "reserved": 0},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#12345678-prod-0002-1234-abcdefghijkl", "type": "products", "quantity": 2, "reserved": 1, "reservedDetails": [{"name": "Test User"}]}
    ]

    for item in items:
        table.put_item(TableName='lists-unittest', Item=item)

    yield
    mock.stop()


class TestGetUsersName:
    def test_get_users_name(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        name = reserve.get_users_name('lists-unittest', user_id)
        assert name == "Test User", "User's name was not as expected."

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

        expected_result = {'quantity': 1, 'reserved': 0}
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
    def test_when_reservedDetails_not_present(self, dynamodb_mock):
        table_name = 'lists-unittest'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        users_name = 'Test User'
        request_reserve = 1
        current_reserved = 0
        total_reserved = 1
        message = 'A test message'
        assert reserve.add_reserved_details(table_name, list_id, product_id, user_id, users_name, request_reserve, current_reserved, total_reserved, message)

        # Check the table was updated with right reserved details
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        reserved_quantity = int(test_response['Item']['reserved']['N'])
        reserved_details = test_response['Item']['reservedDetails']['L']
        reserved_obj = reserved_details[0]['M']

        assert reserved_quantity == 1, "Quantity not as expected."
        assert len(reserved_details) == 1, "Number of reserved details was not as expected."
        assert reserved_obj['name']['S'] == 'Test User', "Reserved name was not as expected."

    def test_with_reserved_details_present(self, dynamodb_mock):
        table_name = 'lists-unittest'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0002-1234-abcdefghijkl'
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        users_name = 'Test User'
        request_reserve = 1
        current_reserved = 1
        total_reserved = 2
        message = 'A test message'
        assert reserve.add_reserved_details(table_name, list_id, product_id, user_id, users_name, request_reserve, current_reserved, total_reserved, message)

        # Check the table was updated with right reserved details
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        # print("reserved details: " + json.dumps(test_response['Item']['reservedDetails']))

        reserved_quantity = int(test_response['Item']['reserved']['N'])
        reserved_details = test_response['Item']['reservedDetails']['L']
        reserved_obj = reserved_details[1]['M']

        assert reserved_quantity == 2, "Quantity not as expected."
        assert len(reserved_details) == 2, "Number of reserved details was not as expected."
        assert reserved_obj['name']['S'] == 'Test User', "Reserved name was not as expected."
        assert reserved_obj['userId']['S'] == '12345678-user-0001-1234-abcdefghijkl', "UserId was not as expected."
        assert reserved_obj['reserved']['N'] == '1', "Reserved quantity was not as expected."
        assert reserved_obj['message']['S'] == 'A test message', "Message was not as expected."
        assert len(reserved_obj['reservedAt']['N']) == 10, "Message was not as expected."


class TestUpdateProductMain:
    def test_reserve_product_not_yet_reserved(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = reserve.update_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['reserved'], "Reserve response was not true."

        # Check the table was updated with right reserved details
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')
        list_id = api_gateway_event['pathParameters']['id']
        product_id = api_gateway_event['pathParameters']['productid']

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        reserved_quantity = int(test_response['Item']['reserved']['N'])
        reserved_details = test_response['Item']['reservedDetails']['L']
        reserved_obj = reserved_details[0]['M']

        assert reserved_quantity == 1, "Quantity not as expected."
        assert len(reserved_details) == 1, "Number of reserved details was not as expected."
        assert reserved_obj['name']['S'] == 'Test User', "Reserved name was not as expected."

    def test_reserve_product_with_one_reserved(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        api_gateway_event['pathParameters']['productid'] = '12345678-prod-0002-1234-abcdefghijkl'

        response = reserve.update_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['reserved'], "Reserve response was not true."

        # Check the table was updated with right reserved details
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')
        list_id = api_gateway_event['pathParameters']['id']
        product_id = api_gateway_event['pathParameters']['productid']

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        reserved_quantity = int(test_response['Item']['reserved']['N'])
        reserved_details = test_response['Item']['reservedDetails']['L']
        reserved_obj = reserved_details[1]['M']

        assert reserved_quantity == 2, "Quantity not as expected."
        assert len(reserved_details) == 2, "Number of reserved details was not as expected."
        assert reserved_obj['name']['S'] == 'Test User', "Reserved name was not as expected."
        assert reserved_obj['userId']['S'] == '12345678-user-0001-1234-abcdefghijkl', "UserId was not as expected."
        assert reserved_obj['reserved']['N'] == '1', "Reserved quantity was not as expected."

    def test_over_reserve_product(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        api_gateway_event['body'] = "{\n    \"quantity\": 2,\n    \"message\": \"Happy birthday to you!\"\n}"

        response = reserve.update_product_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Reserved product quantity 2 exceeds quantity required 1.', "Reserve error was not as expected."


def test_handler(api_gateway_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = reserve.handler(api_gateway_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['reserved']
