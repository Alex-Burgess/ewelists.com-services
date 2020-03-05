import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import delete, logger
from tests import fixtures

log = logger.setup_logger()


@pytest.fixture
def api_gateway_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}

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


class TestDeleteItems:
    def test_delete_list_item(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        items = [
            {"PK": {'S': "LIST#{}".format(list_id)}, 'SK': {'S': "USER#{}".format(user_id)}},
        ]

        assert delete.delete_items('lists-unittest', user_id, list_id, items)

    def test_delete_product_item(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        items = [
            {"PK": {'S': "LIST#{}".format(list_id)}, 'SK': {'S': "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "quantity": 1, "reserved": 0}
        ]

        assert delete.delete_items('lists-unittest', user_id, list_id, items)

    def test_delete_multiple_list_items(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        item_keys = [
            {"PK": {'S': "LIST#{}".format(list_id)}, 'SK': {'S': "USER#{}".format(user_id)}},
            {"PK": {'S': "LIST#{}".format(list_id)}, 'SK': {'S': "PRODUCT#{}".format(product_id)}}
        ]

        assert delete.delete_items('lists-unittest', user_id, list_id, item_keys)

    # @pytest.mark.skip(reason="Moto is not throwing an exception when deleting with ConditionExpression")
    # def test_delete_item_no_list(self, dynamodb_mock):
    #     user_id = '12345678-user-0001-1234-abcdefghijkl'
    #     list_id = '12345678-list-0009-1234-abcdefghijkl'
    #
    #     with pytest.raises(Exception) as e:
    #         delete.delete_item('lists-unittest', user_id, list_id)
    #     assert str(e.value) == "List does not exist.", "Exception not as expected."


class TestGetItemsAssociatedWithList:
    def test_get_items_associated_with_list(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        items = delete.get_items_associated_with_list('lists-unittest', list_id)
        assert len(items) == 13, "Number of items deleted was not as expected."


class TestDeleteMain:
    def test_delete_main(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = delete.delete_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['deleted'], "Delete main response did not contain the correct status."
        assert len(body['listId']) == 36, "Create main response did not contain a listId."

    def test_delete_main_with_bad_table_name(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = delete.delete_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Unexpected error when getting lists from table.', "Create main response did not contain the correct error message."

    def test_delete_main_with_bad_user(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"
        response = delete.delete_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Owner of List ID 12345678-list-0001-1234-abcdefghijkl did not match user id of requestor: 12345678-user-0003-1234-abcdefghijkl.', "Create main response did not contain the correct error message."

    def test_delete_main_with_bad_list(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['id'] = "12345678-list-0100-1234-abcdefghijkl"

        response = delete.delete_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == 'No list exists with this ID.', "Create main response did not contain the correct error message."


def test_handler(api_gateway_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = delete.handler(api_gateway_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    assert re.match('{"deleted": .*}', response['body']), "Response body was not as expected."

    body = json.loads(response['body'])
    assert body['count'] == 13, "Number of items deleted was not as expected."
