import pytest
import os
import json
import boto3
from moto import mock_dynamodb2
from lists import purchase, logger
from tests import fixtures

log = logger.setup_logger()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
    monkeypatch.setitem(os.environ, 'TEMPLATE_NAME', 'Email-Template')
    monkeypatch.setitem(os.environ, 'DOMAIN_NAME', 'https://test.ewelists.com')

    return monkeypatch


@pytest.fixture
def api_gateway_event_no_account_user():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/lists/{id}/purchased/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/purchase/12345678-prod-0001-1234-abcdefghijkl/email/test.user99@gmail.com"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
    event['body'] = json.dumps({
        "quantity": 2,
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
def api_gateway_event_existing_user():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/lists/{id}/purchased/{productid}/email/{email}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/purchase/12345678-prod-0001-1234-abcdefghijkl/email/test.user1@gmail.com"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user1@gmail.com"}
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


class TestNewReservedQuantity:
    def test_new_reserved_quantity(self):
        assert purchase.new_reserved_quantity(1, 1) == 0, "New quantity not as expected."
        assert purchase.new_reserved_quantity(2, 1) == 1, "New quantity not as expected."


class TestNewPurchasedQuantity:
    def test_new_purchased_quantity(self):
        assert purchase.new_purchased_quantity(0, 1) == 1, "New quantity not as expected."
        assert purchase.new_purchased_quantity(2, 1) == 3, "New quantity not as expected."


class TestCreateEmailData:
    def test_create_email_data(self):
        domain_name = 'http://localhost:3000'
        name = 'Test User'
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

        data = purchase.create_email_data(domain_name, name, list_id, list_title, quantity, product)

        expected_data = {
            "name": "Test User",
            "list_title": "Test List Title",
            "list_url": "http://localhost:3000/lists/12345678-list-0001-1234-abcdefghijkl",
            "quantity": 2,
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "product_url": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "image_url": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }

        assert len(data) == 8, "Number of fields in email data was not as expected."
        assert data == expected_data, "Email data json object was not as expected."


class TestReserveMain:
    def test_no_list_id_path_parameter(self, env_vars, api_gateway_event_existing_user):
        api_gateway_event_existing_user['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "null", "email": "test.user99@gmail.com"}
        response = purchase.purchase_main(api_gateway_event_existing_user)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null id parameter.', "Error for missing environment variable was not as expected."

    def test_no_product_id_path_parameter(self, env_vars, api_gateway_event_existing_user):
        api_gateway_event_existing_user['pathParameters'] = {"productid": "null", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        response = purchase.purchase_main(api_gateway_event_existing_user)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null productid parameter.', "Error for missing environment variable was not as expected."

    def test_no_email_path_parameter(self, env_vars, api_gateway_event_existing_user):
        api_gateway_event_existing_user['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "null"}
        response = purchase.purchase_main(api_gateway_event_existing_user)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null email parameter.', "Error for missing environment variable was not as expected."

    def test_confirm_product_already_confirmed_by_user_with_account(self, env_vars, api_gateway_event_existing_user, dynamodb_mock):
        api_gateway_event_existing_user['pathParameters'] = {"productid": "12345678-prod-0004-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user2@gmail.com"}
        response = purchase.purchase_main(api_gateway_event_existing_user)
        body = json.loads(response['body'])
        assert body['error'] == 'Product was already purchased.', "Error for missing environment variable was not as expected."

    def test_confirm_product_already_confirmed_by_user_with_no_account(self, env_vars, api_gateway_event_no_account_user, dynamodb_mock):
        api_gateway_event_no_account_user['pathParameters'] = {"productid": "12345678-prod-0005-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        response = purchase.purchase_main(api_gateway_event_no_account_user)
        body = json.loads(response['body'])
        assert body['error'] == 'Product was already purchased.', "Error for missing environment variable was not as expected."

    def test_confirm_product_that_was_unreserved(self, env_vars, api_gateway_event_existing_user, dynamodb_mock):
        api_gateway_event_existing_user['pathParameters'] = {"productid": "12345678-prod-1000-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user1@gmail.com"}
        response = purchase.purchase_main(api_gateway_event_existing_user)
        body = json.loads(response['body'])
        assert body['error'] == 'Product is not reserved by user.', "Error for missing environment variable was not as expected."

    def test_reserve_no_name_for_non_user(self, env_vars, api_gateway_event_no_account_user, dynamodb_mock):
        api_gateway_event_no_account_user['body'] = json.dumps({
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

        response = purchase.purchase_main(api_gateway_event_no_account_user)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event did not contain a name body attribute.', "Reserve error was not as expected."

    def test_reserve_with_no_body(self, env_vars, api_gateway_event_no_account_user, dynamodb_mock):
        api_gateway_event_no_account_user['body'] = None

        response = purchase.purchase_main(api_gateway_event_no_account_user)
        body = json.loads(response['body'])
        assert body['error'] == 'Body was missing required attributes.', "Reserve error was not as expected."


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
def test_handler_with_existing_user(api_gateway_event_existing_user, env_vars, dynamodb_mock):
    response = purchase.handler(api_gateway_event_existing_user, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert body['purchased'], "purchase was not confirmed."


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
def test_handler_with_no_account_user(api_gateway_event_no_account_user, env_vars, dynamodb_mock):
    response = purchase.handler(api_gateway_event_no_account_user, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert body['purchased'], "purchase was not confirmed."