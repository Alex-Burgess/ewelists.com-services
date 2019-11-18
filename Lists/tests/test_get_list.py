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

    # 2 Users.  User 1 owns 1 list with 3 products, that is shared with 1 other user.  user 2 owns 1 list with 0 products and is not shared with anyone.
    items = [
        {"PK": "USER#12345678-user-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "email": "test.user@gmail.com", "name": "Test User", "userId": "12345678-user-0001-1234-abcdefghijkl"},
        {"PK": "USER#12345678-user-0002-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "email": "test.user2@gmail.com", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 2019 Christmas List", "occasion": "Christmas", "listId": "12345678-list-0002-1234-abcdefghijkl", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "eventDate": "25 December 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 2019 Christmas List", "occasion": "Christmas", "listId": "12345678-list-0002-1234-abcdefghijkl", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "eventDate": "25 December 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's New Christmas List", "occasion": "Christmas", "listId": "12345678-list-0003-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's New Christmas List", "occasion": "Christmas", "listId": "12345678-list-0003-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1000", "quantity": 1, "reserved": 0, "type": "products"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1001", "quantity": 1, "reserved": 1, "type": "products"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1002", "quantity": 2, "reserved": 1, "type": "notfound"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "RESERVED#PRODUCT#1001", "name": "Test User2", "userId": "12345678-user-0005-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday to you", "reservedAt": "1573739580"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "RESERVED#PRODUCT#1002", "name": "Test User1", "userId": "12345678-user-0004-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday", "reservedAt": "1573739584"}
    ]

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
        assert len(items) == 8, "Number of items returned was not as expected."

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

        assert body['list']['listId'] == "12345678-list-0001-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert body['list']['title'] == "Api Child's 1st Birthday", "Get list response did not contain a title."
        assert body['list']['description'] == "A gift list for Api Childs birthday.", "Get list response did not contain a description."
        assert body['list']['eventDate'] == "01 September 2019", "Get list response did not contain a date."
        assert body['list']['occasion'] == "Birthday", "Get list response did not contain an occasion."
        assert body['list']['imageUrl'] == "/images/celebration-default.jpg", "Get list response did not contain an imageUrl."

        assert len(body['products']) == 3, "Get list response did not contain correct number of products."
        assert body['products']["1000"] == {"productId": "1000", "quantity": 1, "reserved": 0, "type": "products"}, "Product object not correct."
        assert body['products']["1001"] == {"productId": "1001", "quantity": 1, "reserved": 1, "type": "products"}, "Product object not correct."
        assert body['products']["1002"] == {"productId": "1002", "quantity": 2, "reserved": 1, "type": "notfound"}, "Product object not correct."

        assert body['reserved'][0] == {"productId": "1001", "name": "Test User2", "userId": "12345678-user-0005-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday to you"}, "Reserved object not correct."
        assert body['reserved'][1] == {"productId": "1002", "name": "Test User1", "userId": "12345678-user-0004-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday"}, "Reserved object not correct."

    def test_get_list_with_no_date(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_get_list_event['pathParameters']['id'] = "12345678-list-0003-1234-abcdefghijkl"

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0003-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert 'eventDate' not in body['list'], "List date was not empty."
        assert body['list']['occasion'] == "Christmas", "Get list response did not contain an occasion."

    def test_get_list_main_wrong_table(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting list item from table.', "Get list response did not contain the correct error message."

    def test_get_list_that_requestor_does_not_own(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_get_list_event['pathParameters']['id'] = "12345678-list-0002-1234-abcdefghijkl"

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == "Owner of List ID 12345678-list-0002-1234-abcdefghijkl did not match user id of requestor: 12345678-user-0001-1234-abcdefghijkl.", "Get list response did not contain the correct error message."


def test_handler(api_gateway_get_list_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = get_list.handler(api_gateway_get_list_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"list": .*}', response['body'])
