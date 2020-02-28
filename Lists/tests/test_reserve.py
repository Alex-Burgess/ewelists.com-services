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
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
    monkeypatch.setitem(os.environ, 'TEMPLATE_NAME', 'Email-Template')
    monkeypatch.setitem(os.environ, 'DOMAIN_NAME', 'https://test.ewelists.com')

    return monkeypatch


@pytest.fixture
def api_gateway_event_prod1():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = json.dumps({
        "quantity": 2,
        "title": "Child User1 1st Birthday",
        "product": {
            "type": "products",
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "productUrl": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "imageUrl": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }
    })

    return event


@pytest.fixture
def api_gateway_event_prod2():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0002-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0002-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = json.dumps({
        "quantity": 1,
        "title": "Child User1 1st Birthday",
        "product": {
            "type": "products",
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "productUrl": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "imageUrl": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }
    })

    return event


@pytest.fixture
def api_gateway_event_existing_user():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}/email/{email}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/test.user1@gmail.com"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user1@gmail.com"}
    event['body'] = json.dumps({
        "quantity": 1,
        "title": "Child User1 1st Birthday",
        "name": "Test User1",
        "product": {
            "type": "products",
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "productUrl": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "imageUrl": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }
    })

    return event


@pytest.fixture
def dynamodb_mock():
    mock = mock_dynamodb2()
    mock.start()
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = dynamodb.create_table(
        TableName='lists-unittest',
        KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}, {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{'AttributeName': 'PK', 'AttributeType': 'S'}, {'AttributeName': 'SK', 'AttributeType': 'S'}, {'AttributeName': 'email', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
        GlobalSecondaryIndexes=[{
            'IndexName': 'email-index',
            'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
            'Projection': {
                'ProjectionType': 'ALL'
            }
        }]
    )

    items = fixtures.load_test_data()

    for item in items:
        table.put_item(TableName='lists-unittest', Item=item)

    yield
    mock.stop()


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
class TestCreateReservation:
    def test_create_reservation(self, dynamodb_mock):
        user = {
            'id': '12345678-user-0002-1234-abcdefghijkl',
            'email': 'test.user2@gmail.com',
            'name': 'Test User2'
        }

        resv_id = '12345678-resv-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        list_title = 'Child User1 1st Birthday'
        product_id = '12345678-prod-0002-1234-abcdefghijkl'
        new_product_reserved_quantity = 1
        request_reserve_quantity = 1

        assert reserve.create_reservation('lists-unittest', resv_id, list_id, list_title, product_id, new_product_reserved_quantity, request_reserve_quantity, user)

    def test_create_reservation_with_email(self, dynamodb_mock):
        user = {
            'id': 'test.user10@gmail.com',
            'email': 'test.user10@gmail.com',
            'name': 'Test User10'
        }

        resv_id = '12345678-resv-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        list_title = 'Child User1 1st Birthday'
        product_id = '12345678-prod-0002-1234-abcdefghijkl'
        new_product_reserved_quantity = 1
        request_reserve_quantity = 1

        assert reserve.create_reservation('lists-unittest', resv_id, list_id, list_title, product_id, new_product_reserved_quantity, request_reserve_quantity, user)


class TestCreateEmailData:
    def test_create_email_data(self):
        domain_name = 'http://localhost:3000'
        name = 'Test User'
        resv_id = '12345678-resv-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        list_title = 'Test List Title'
        quantity = 2
        product = {
            "type": "products",
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "productUrl": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "imageUrl": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }

        data = reserve.create_email_data(domain_name, name, resv_id, list_id, list_title, quantity, product)

        expected_data = {
            "name": "Test User",
            "list_title": "Test List Title",
            "list_url": "http://localhost:3000/lists/12345678-list-0001-1234-abcdefghijkl",
            "quantity": 2,
            "confirm_url": "http://localhost:3000/purchased/12345678-resv-0001-1234-abcdefghijkl",
            "edit_url": "http://localhost:3000/edit-reservation/12345678-resv-0001-1234-abcdefghijkl",
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "product_url": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "image_url": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }

        assert len(data) == 10, "Number of fields in email data was not as expected."
        assert data == expected_data, "Email data json object was not as expected."


class TestReserveMain:
    @pytest.mark.skip(reason="transact_write_items is not implemented for moto. https://github.com/spulec/moto/issues/2424")
    def test_reserve_product_not_yet_reserved(self, env_vars, api_gateway_event_prod2, dynamodb_mock):
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
        assert reserved_details_response['Item']['SK']['S'] == 'RESERVED#12345678-prod-0002-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl', "SK not as expected."
        assert reserved_details_response['Item']['quantity']['N'] == '1', "Quantity not as expected."

    @pytest.mark.skip(reason="transact_write_items is not implemented for moto")
    def test_reserve_product_with_one_reserved(self, env_vars, api_gateway_event_prod1, dynamodb_mock):
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

    def test_over_reserve_product(self, env_vars, api_gateway_event_prod1, dynamodb_mock):
        api_gateway_event_prod1['body'] = json.dumps({
            "quantity": 4,
            "title": "Child User1 1st Birthday",
            "product": {
                "type": "products",
                "brand": "Mamas and Papas",
                "details": "Balloon Print Zip All-in-One",
                "productUrl": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
                "imageUrl": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
            }
        })

        response = reserve.reserve_main(api_gateway_event_prod1)
        body = json.loads(response['body'])
        assert body['error'] == 'Reserved quantity for product (2) could not be updated by 4 as exceeds required quantity (3).', "Reserve error was not as expected."

    def test_reserve_product_not_added_to_list(self, env_vars, api_gateway_event_prod1, dynamodb_mock):
        api_gateway_event_prod1['pathParameters'] = {"productid": "12345678-prod-0100-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}

        response = reserve.reserve_main(api_gateway_event_prod1)
        body = json.loads(response['body'])
        assert body['error'] == 'No product item exists with this ID.', "Reserve error was not as expected."

    def test_reserve_product_already_reserved_by_user(self, env_vars, api_gateway_event_prod1, dynamodb_mock):
        api_gateway_event_prod1['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0002-1234-abcdefghijkl"

        response = reserve.reserve_main(api_gateway_event_prod1)
        body = json.loads(response['body'])
        assert body['error'] == 'Product already reserved by user.', "Reserve error was not as expected."

    def test_reserve_with_user_that_has_account(self, env_vars, api_gateway_event_existing_user, dynamodb_mock):
        response = reserve.reserve_main(api_gateway_event_existing_user)
        body = json.loads(response['body'])
        assert body['error'] == 'User has an account, login required before product can be reserved.', "Reserve error was not as expected."


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
def test_handler(api_gateway_event_prod1, env_vars, dynamodb_mock):
    response = reserve.handler(api_gateway_event_prod1, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['reserved']
