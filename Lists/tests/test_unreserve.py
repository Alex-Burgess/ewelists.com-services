import pytest
import os
import json
import boto3
from moto import mock_dynamodb2
from lists import unreserve, logger
from tests import fixtures

log = logger.setup_logger()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')

    return monkeypatch


@pytest.fixture
def api_gateway_event_with_account():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/test.user3@gmail.com"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user3@gmail.com"}

    return event


@pytest.fixture
def api_gateway_event_with_no_account():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}/email/{email}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/test.user99@gmail.com"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}

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
    # teardown: stop moto server
    mock.stop()


class TestCreateReservationKey:
    def test_create_product_key(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0001-1234-abcdefghijkl'

        expected_object = {
            ':PK': {'S': "LIST#12345678-list-0001-1234-abcdefghijkl"},
            ':SK': {'S': "RESERVED#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0001-1234-abcdefghijkl"}
        }

        key = unreserve.create_condition(list_id, product_id, user_id)
        assert key == expected_object, "Key was not as expected."


class TestUnreserveMain:
    def test_no_list_id_path_parameter(self, env_vars, api_gateway_event_with_account):
        api_gateway_event_with_account['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "null", "email": "test.user99@gmail.com"}
        response = unreserve.unreserve_main(api_gateway_event_with_account)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null id parameter.', "Error for missing environment variable was not as expected."

    def test_no_product_id_path_parameter(self, env_vars, api_gateway_event_with_account):
        api_gateway_event_with_account['pathParameters'] = {"productid": "null", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        response = unreserve.unreserve_main(api_gateway_event_with_account)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null productid parameter.', "Error for missing environment variable was not as expected."

    def test_no_email_path_parameter(self, env_vars, api_gateway_event_with_account):
        api_gateway_event_with_account['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "null"}
        response = unreserve.unreserve_main(api_gateway_event_with_account)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null email parameter.', "Error for missing environment variable was not as expected."

    @pytest.mark.skip(reason="transact_write_items is not implemented for moto")
    def test_unreserve_product_for_user(self, env_vars, dynamodb_mock, api_gateway_event_with_account):
        response = unreserve.unreserve_main(api_gateway_event_with_account)
        body = json.loads(response['body'])
        assert body['unreserved'], "Unreserve main response did not contain the correct status."

    def test_unreserve_product_not_reserved_by_requestor(self, env_vars, dynamodb_mock, api_gateway_event_with_account):
        api_gateway_event_with_account['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0011-1234-abcdefghijkl", "email": "test.user30@gmail.com"}
        response = unreserve.unreserve_main(api_gateway_event_with_account)
        body = json.loads(response['body'])
        assert body['error'] == "Product is not reserved by user.", "Error was not as expected"

    def test_unreserve_product_already_confirmed(self, env_vars, dynamodb_mock, api_gateway_event_with_account):
        api_gateway_event_with_account['pathParameters'] = {"productid": "12345678-prod-0005-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        response = unreserve.unreserve_main(api_gateway_event_with_account)
        body = json.loads(response['body'])
        assert body['error'] == "Product was already purchased.", "Error was not as expected"

    def test_unreserve_product_with_wrong_quantities(self, env_vars, dynamodb_mock, api_gateway_event_with_account):
        # Update table to break concurrency of product reserved quantity, with that of the reserved items.
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')
        key = {
            'PK': {'S': "LIST#{}".format(api_gateway_event_with_account['pathParameters']['id'])},
            'SK': {'S': "PRODUCT#{}".format(api_gateway_event_with_account['pathParameters']['productid'])}
        }

        response = dynamodb.update_item(
            TableName='lists-unittest',
            Key=key,
            UpdateExpression="set reserved = :r",
            ExpressionAttributeValues={
                ':r': {'N': str(0)},
            }
        )

        response = unreserve.unreserve_main(api_gateway_event_with_account)
        body = json.loads(response['body'])
        assert body['error'] == "Reserved quantity for product (0) could not be updated by -1.", "Error was not as expected"


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
def test_handler(api_gateway_event_with_account, env_vars, dynamodb_mock):
    response = unreserve.handler(api_gateway_event_with_account, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['reserved']


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
def test_handler_with_email(api_gateway_event_with_no_account, env_vars, dynamodb_mock):
    response = unreserve.handler(api_gateway_event_with_no_account, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['reserved']
