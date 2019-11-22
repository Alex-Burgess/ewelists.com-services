import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import unshare
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_unshare_shared_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/share/{user}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/share/12345678-user-0002-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"user": "12345678-user-0002-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"share_type\": \"SHARED\"\n}"

    return event


@pytest.fixture
def api_gateway_unshare_pending_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/share/{user}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/share/test.user4%40gmail.com"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"user": "test.user4%40gmail.com", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"share_type\": \"PENDING\"\n}"

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


class TestDeleteSharedItem:
    def test_delete_shared_item(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        assert unshare.delete_shared_item('lists-unittest', list_id, user_id), "Delete item was not successful."

    def test_delete_shared_item_with_no_table(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            unshare.delete_shared_item('lists-unittes', list_id, user_id)
        assert str(e.value) == "Shared user could not be deleted.", "Exception not as expected."

    def test_delete_which_does_not_exist(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0020-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            unshare.delete_shared_item('lists-unittest', list_id, user_id)
        assert str(e.value) == "Shared user could not be deleted.", "Exception not as expected."


class TestDeletePendingItem:
    def test_delete_pending_item(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        email = 'test.user4@gmail.com'
        assert unshare.delete_pending_item('lists-unittest', list_id, email), "Delete item was not successful."

    def test_delete_pending_item_with_no_table(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        email = 'test.user4@gmail.com'

        with pytest.raises(Exception) as e:
            unshare.delete_pending_item('lists-unittes', list_id, email)
        assert str(e.value) == "Pending shared user could not be deleted.", "Exception not as expected."

    def test_delete_which_does_not_exist(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        email = 'test.user40@gmail.com'

        with pytest.raises(Exception) as e:
            unshare.delete_pending_item('lists-unittest', list_id, email)
        assert str(e.value) == "Pending shared user could not be deleted.", "Exception not as expected."


class TestUnshareMain:
    def test_unshare_shared_user(self, api_gateway_unshare_shared_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unshare.unshare_main(api_gateway_unshare_shared_event)
        body = json.loads(response['body'])
        assert body['unshared'], "Unshare main response did not contain the correct status."

    def test_unshare_pending_user(self, api_gateway_unshare_pending_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unshare.unshare_main(api_gateway_unshare_pending_event)
        body = json.loads(response['body'])
        assert body['unshared'], "Unshare main response did not contain the correct status."

    def test_with_wrong_type(self, api_gateway_unshare_pending_event, monkeypatch, dynamodb_mock):
        api_gateway_unshare_pending_event['body'] = "{\n    \"share_type\": \"WRONG\"\n}"
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unshare.unshare_main(api_gateway_unshare_pending_event)
        body = json.loads(response['body'])
        assert body['error'] == "API Event did not contain a share type of SHARED or PENDING.", "Unshare main response did not contain the correct status."

    def test_pending_user_did_not_exist(self, api_gateway_unshare_pending_event, monkeypatch, dynamodb_mock):
        api_gateway_unshare_pending_event['pathParameters'] = {"user": "test.user44%40gmail.com", "id": "12345678-list-0001-1234-abcdefghijkl"}
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unshare.unshare_main(api_gateway_unshare_pending_event)
        body = json.loads(response['body'])
        assert body['error'] == "Pending shared user could not be deleted.", "Unshare main response did not contain the correct status."

    def test_shared_user_did_not_exist(self, api_gateway_unshare_shared_event, monkeypatch, dynamodb_mock):
        api_gateway_unshare_shared_event['pathParameters'] = {"user": "12345678-user-0200-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unshare.unshare_main(api_gateway_unshare_shared_event)
        body = json.loads(response['body'])
        assert body['error'] == "Shared user could not be deleted.", "Unshare main response did not contain the correct status."

    def test_list_did_not_exist(self, api_gateway_unshare_shared_event, monkeypatch, dynamodb_mock):
        api_gateway_unshare_shared_event['pathParameters'] = {"user": "12345678-user-0002-1234-abcdefghijkl", "id": "12345678-list-0100-1234-abcdefghijkl"}
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unshare.unshare_main(api_gateway_unshare_shared_event)
        body = json.loads(response['body'])
        assert body['error'] == "No list exists with this ID.", "Unshare main response did not contain the correct status."

    def test_user_did_not_own_list(self, api_gateway_unshare_shared_event, monkeypatch, dynamodb_mock):
        user = '12345678-user-0010-1234-abcdefghijkl'
        api_gateway_unshare_shared_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:" + user

        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unshare.unshare_main(api_gateway_unshare_shared_event)
        body = json.loads(response['body'])
        assert body['error'] == "No list exists with this ID.", "Unshare main response did not contain the correct status."


class TestHandler:
    def test_handler_shared_user(self, api_gateway_unshare_shared_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unshare.handler(api_gateway_unshare_shared_event, None)
        assert response['statusCode'] == 200, "Response statusCode was not as expected."
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
        assert re.match('{"unshared": .*}', response['body']), "Response body was not as expected."

    def test_handler_pending_user(self, api_gateway_unshare_pending_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unshare.handler(api_gateway_unshare_pending_event, None)
        assert response['statusCode'] == 200, "Response statusCode was not as expected."
        assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
        assert re.match('{"unshared": .*}', response['body']), "Response body was not as expected."
