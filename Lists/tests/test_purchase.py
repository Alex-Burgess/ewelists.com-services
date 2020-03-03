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
    # monkeypatch.setitem(os.environ, 'TEMPLATE_NAME', 'Email-Template')
    # monkeypatch.setitem(os.environ, 'DOMAIN_NAME', 'https://test.ewelists.com')

    return monkeypatch


@pytest.fixture
def api_gateway_event():
    # User 2 will update its reserved quantity of product 1 from 1 to 2.
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/purchased/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/purchase/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0002-1234-abcdefghijkl"

    return event


@pytest.fixture
def api_gateway_event_existing_user():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/lists/{id}/purchased/{productid}/email/{email}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/purchase/12345678-prod-0001-1234-abcdefghijkl/email/test.user1@gmail.com"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user1@gmail.com"}

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


# @pytest.mark.skip(reason="transact_write_items is not implemented for moto")
def test_handler(api_gateway_event, env_vars, dynamodb_mock):
    response = purchase.handler(api_gateway_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    assert body['purchased']
