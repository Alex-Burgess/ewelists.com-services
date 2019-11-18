import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import get_shared_list
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

    # 3 users.  user 1 owns list 1 and is shared with user 2. user 1 owns list 2 which is not shared.  user 3 has no lists shared with them.
    items = [
        {"PK": "USER#12345678-user-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "email": "test.user@gmail.com", "name": "Test User", "userId": "12345678-user-0001-1234-abcdefghijkl"},
        {"PK": "USER#12345678-user-0002-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "email": "test.user2@gmail.com", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl"},
        {"PK": "USER#12345678-user-0003-1234-abcdefghijkl", "SK": "USER#12345678-user-0003-1234-abcdefghijkl", "email": "test.user3@gmail.com", "name": "Test User3", "userId": "12345678-user-0003-1234-abcdefghijkl"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's 2019 Christmas List", "occasion": "Christmas", "listId": "12345678-list-0002-1234-abcdefghijkl", "listOwner": "1234250a-0fb0-4b32-9842-041c69be1234", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "eventDate": "25 December 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's 2019 Christmas List", "occasion": "Christmas", "listId": "12345678-list-0002-1234-abcdefghijkl", "listOwner": "1234250a-0fb0-4b32-9842-041c69be1234", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "eventDate": "25 December 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's New Christmas List", "occasion": "Christmas", "listId": "12345678-list-0003-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's New Christmas List", "occasion": "Christmas", "listId": "12345678-list-0003-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's New Christmas List", "occasion": "Christmas", "listId": "12345678-list-0003-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl", "quantity": 1, "reserved": 0, "type": "products"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#12345678-prod-0002-1234-abcdefghijkl", "quantity": 2, "reserved": 0, "type": "products"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#12345678-prod-0003-1234-abcdefghijkl", "quantity": 2, "reserved": 1, "type": "notfound"}
    ]

    for item in items:
        table.put_item(TableName='lists-unittest', Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetListQuery:
    def test_get_list_query(self, dynamodb_mock):
        user_id = "12345678-user-0002-1234-abcdefghijkl"
        list_id = "12345678-list-0001-1234-abcdefghijkl"
        items = get_shared_list.get_list_query('lists-unittest', user_id, list_id)
        assert len(items) == 6, "Number of items deleted was not as expected."

    def test_get_list_query_no_table_name(self, dynamodb_mock):
        user_id = "12345678-user-0002-1234-abcdefghijkl"
        list_id = "12345678-list-0001-1234-abcdefghijkl"

        with pytest.raises(Exception) as e:
            get_shared_list.get_list_query('lists-unittes', user_id, list_id)
        assert str(e.value) == "Unexpected error when getting list item from table.", "Exception not as expected."

    def test_get_list_query_for_item_that_does_not_exist(self, dynamodb_mock):
        user_id = "12345678-user-0002-1234-abcdefghijkl"
        list_id = "12345678-list-0009-1234-abcdefghijkl"

        with pytest.raises(Exception) as e:
            get_shared_list.get_list_query('lists-unittest', user_id, list_id)
        assert str(e.value) == "No query results for List ID 12345678-list-0009-1234-abcdefghijkl and user: 12345678-user-0002-1234-abcdefghijkl.", "Exception not as expected."


class TestGetSharedListMain:
    def test_get_shared_list_main(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = get_shared_list.get_shared_list_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0001-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert body['list']['title'] == "Api Child's 1st Birthday", "Get list response did not contain a title."
        assert body['list']['description'] == "A gift list for Api Childs birthday.", "Get list response did not contain a description."
        assert body['list']['eventDate'] == "01 September 2019", "Get list response did not contain a date."
        assert body['list']['occasion'] == "Birthday", "Get list response did not contain an occasion."
        assert body['list']['imageUrl'] == "/images/celebration-default.jpg", "Get list response did not contain an imageUrl."
        assert len(body['products']) == 3, "Get list response did not contain correct number of products."

        assert body['products']["12345678-prod-0001-1234-abcdefghijkl"] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "quantity": 1, "reserved": 0, "type": "products"}, "Product object not correct."
        assert body['products']["12345678-prod-0002-1234-abcdefghijkl"] == {"productId": "12345678-prod-0002-1234-abcdefghijkl", "quantity": 2, "reserved": 0, "type": "products"}, "Product object not correct."
        assert body['products']["12345678-prod-0003-1234-abcdefghijkl"] == {"productId": "12345678-prod-0003-1234-abcdefghijkl", "quantity": 2, "reserved": 1, "type": "notfound"}, "Product object not correct."

    def test_get_shared_list_with_no_date(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['id'] = "12345678-list-0003-1234-abcdefghijkl"

        response = get_shared_list.get_shared_list_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0003-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert 'eventDate' not in body['list'], "List date was not empty."
        assert body['list']['occasion'] == "Christmas", "Get list response did not contain an occasion."

    def test_get_shared_list_main_no_table(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = get_shared_list.get_shared_list_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting list item from table.', "Get list response did not contain the correct error message."

    def test_get_shared_list_when_not_shared_with_requestor(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"

        response = get_shared_list.get_shared_list_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['error'] == "List ID 12345678-list-0001-1234-abcdefghijkl did not have a shared item with user 12345678-user-0003-1234-abcdefghijkl.", "Get list response did not contain the correct error message."


def test_handler(api_gateway_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = get_shared_list.handler(api_gateway_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"list": .*}', response['body'])
