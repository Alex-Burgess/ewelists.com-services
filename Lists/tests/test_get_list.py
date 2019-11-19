import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import get_list
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_get_list_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl",
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "null"

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


class TestGetListQuery:
    def test_get_list_with_owner(self, dynamodb_mock):
        user_id = "12345678-user-0001-1234-abcdefghijkl"
        list_id = "12345678-list-0001-1234-abcdefghijkl"
        items = get_list.get_list_query('lists-unittest', user_id, list_id)
        assert len(items) == 9, "Number of items returned was not as expected."

    def test_get_list_query_wrong_table(self, dynamodb_mock):
        user_id = "12345678-user-0001-1234-abcdefghijkl"
        list_id = "12345678-list-0001-1234-abcdefghijkl"

        with pytest.raises(Exception) as e:
            get_list.get_list_query('lists-unittes', user_id, list_id)
        assert str(e.value) == "Unexpected error when getting list item from table.", "Exception not as expected."

    def test_get_list_query_with_list_that_does_not_exist(self, dynamodb_mock):
        user_id = "12345678-user-0001-1234-abcdefghijkl"
        list_id = "12345678-list-0009-1234-abcdefghijkl"

        with pytest.raises(Exception) as e:
            get_list.get_list_query('lists-unittest', user_id, list_id)
        assert str(e.value) == "No query results for List ID 12345678-list-0009-1234-abcdefghijkl and user: 12345678-user-0001-1234-abcdefghijkl.", "Exception not as expected."


class TestGetListMain:
    def test_get_list_main(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0001-1234-abcdefghijkl", "ListId was not correct."
        assert body['list']['title'] == "Child User1 1st Birthday", "Title was not correct."
        assert body['list']['description'] == "A gift list for Child User1 birthday.", "Description was not correct."
        assert body['list']['eventDate'] == "31 October 2018", "Event data was not correct."
        assert body['list']['occasion'] == "Birthday", "Occasion was not correct."
        assert body['list']['imageUrl'] == "/images/celebration-default.jpg", "Image url was not correct."

        assert len(body['products']) == 3, "Get list response did not contain correct number of products."
        assert body['products']["12345678-prod-0001-1234-abcdefghijkl"] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "quantity": 3, "reserved": 2, "type": "products"}, "Product object not correct."
        assert body['products']["12345678-prod-0002-1234-abcdefghijkl"] == {"productId": "12345678-prod-0002-1234-abcdefghijkl", "quantity": 1, "reserved": 0, "type": "products"}, "Product object not correct."
        assert body['products']["12345678-notf-0001-1234-abcdefghijkl"] == {"productId": "12345678-notf-0001-1234-abcdefghijkl", "quantity": 2, "reserved": 1, "type": "notfound"}, "Product object not correct."

        assert body['reserved'][0] == {"productId": "12345678-notf-0001-1234-abcdefghijkl", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday"}, "Reserved object not correct."
        assert body['reserved'][1] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday"}, "Reserved object not correct."
        assert body['reserved'][2] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "name": "Test User3", "userId": "12345678-user-0003-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday"}, "Reserved object not correct."

    def test_get_list_with_no_date(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_get_list_event['pathParameters']['id'] = "12345678-list-0002-1234-abcdefghijkl"

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0002-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert 'eventDate' not in body['list'], "List date was not empty."
        assert body['list']['occasion'] == "Christmas", "Get list response did not contain an occasion."

    def test_get_list_main_wrong_table(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting list item from table.', "Get list response did not contain the correct error message."

    def test_get_list_that_requestor_does_not_own(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_get_list_event['pathParameters']['id'] = "12345678-list-0003-1234-abcdefghijkl"

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == "Owner of List ID 12345678-list-0003-1234-abcdefghijkl did not match user id of requestor: 12345678-user-0001-1234-abcdefghijkl.", "Get list response did not contain the correct error message."


def test_handler(api_gateway_get_list_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = get_list.handler(api_gateway_get_list_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"list": .*}', response['body'])
