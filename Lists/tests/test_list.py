import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import list
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
    event['resource'] = "/lists/"
    event['path'] = "/lists",
    event['httpMethod'] = "GET"

    return event


@pytest.fixture
def dynamodb_mock():
    mock = mock_dynamodb2()
    mock.start()

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = dynamodb.create_table(
            TableName='lists-unittest',
            KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}, {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[{'AttributeName': 'PK', 'AttributeType': 'S'}, {'AttributeName': 'SK', 'AttributeType': 'S'}, {'AttributeName': 'userId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
            GlobalSecondaryIndexes=[{
                'IndexName': 'userId-index',
                'KeySchema': [{'AttributeName': 'userId', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
                'Projection': {
                    'ProjectionType': 'ALL'
                }
            }]
        )

    # 3 users. User 1, owns list 1, which is not shared.  user 2, owns list 2 and 3 which are shared with user 1.  User 3 has no lists.
    items = [
        {"PK": "USER#12345678-user-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "email": "test.user@gmail.com", "name": "Test User", "userId": "12345678-user-0001-1234-abcdefghijkl"},
        {"PK": "USER#12345678-user-0002-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "email": "test.user2@gmail.com", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl"},
        {"PK": "USER#12345678-user-0003-1234-abcdefghijkl", "SK": "USER#12345678-user-0003-1234-abcdefghijkl", "email": "test.user3@gmail.com", "name": "Test User3", "userId": "12345678-user-0003-1234-abcdefghijkl"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0002-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars birthday.", "eventDate": "31 October 2018", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0002-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars birthday.", "eventDate": "31 October 2018", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0002-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars birthday.", "eventDate": "31 October 2018", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 2nd Birthday", "occasion": "Birthday", "listId": "12345678-list-0003-1234-abcdefghijkl", "createdAt": "2019-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars 2nd Birthday.", "eventDate": "31 October 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 2nd Birthday", "occasion": "Birthday", "listId": "12345678-list-0003-1234-abcdefghijkl", "createdAt": "2019-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars 2nd Birthday.", "eventDate": "31 October 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's 2nd Birthday", "occasion": "Birthday", "listId": "12345678-list-0003-1234-abcdefghijkl", "createdAt": "2019-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars 2nd Birthday.", "eventDate": "31 October 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1000", "quantity": 1, "reserved": 0, "type": "products"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1001", "quantity": 1, "reserved": 1, "type": "products"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1002", "quantity": 2, "reserved": 1, "type": "notfound"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "RESERVED#PRODUCT#1001", "name": "Test User2", "userId": "12345678-user-0001-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday to you", "reservedAt": "1573739580"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "RESERVED#PRODUCT#1002", "name": "Test User1", "userId": "12345678-user-0001-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday", "reservedAt": "1573739584"}
    ]

    for item in items:
        table.put_item(TableName='lists-unittest', Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetLists:
    def test_get_lists_for_requestor(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        lists_response = list.get_lists('lists-unittest', 'userId-index', user_id)

        test_user = {"email": "test.user@gmail.com"}
        assert lists_response['user'] == test_user, "Test user was not as expected."

        owned_list = {"listId": "12345678-list-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"}
        assert len(lists_response['owned']) == 1, "User should only own 1 list."
        assert lists_response['owned'][0] == owned_list, "Details of the list owned by user was not as expected."

        shared_list1 = {"listId": "12345678-list-0002-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "description": "A gift list for Oscars birthday.", "eventDate": "31 October 2018", "imageUrl": "/images/celebration-default.jpg"}
        shared_list2 = {"listId": "12345678-list-0003-1234-abcdefghijkl", "title": "Oscar's 2nd Birthday", "occasion": "Birthday", "description": "A gift list for Oscars 2nd Birthday.", "eventDate": "31 October 2019", "imageUrl": "/images/celebration-default.jpg"}
        assert len(lists_response['shared']) == 2, "User should only have 2 lists shared with them."
        assert lists_response['shared'][0] == shared_list1, "Details of the list shared with user was not as expected."
        assert lists_response['shared'][1] == shared_list2, "Details of the list shared with user was not as expected."

    def test_get_lists_bad_table_name(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            list.get_lists('lists-unittes', 'userId-index', user_id)
        assert str(e.value) == "Unexpected error when getting lists from table.", "Exception not as expected."

    def test_get_lists_bad_index_name(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            list.get_lists('lists-unittest', 'userId-inde', user_id)
        assert str(e.value) == "Unexpected error when getting lists from table.", "Exception not as expected."

    def test_get_lists_for_user_with_no_lists(self, dynamodb_mock):
        user_id = '12345678-user-0003-1234-abcdefghijkl'
        lists_response = list.get_lists('lists-unittest', 'userId-index', user_id)
        assert len(lists_response['owned']) == 0, "Number of lists was not 0."
        assert len(lists_response['shared']) == 0, "Number of lists was not 0."


class TestListMain:
    def test_list_main(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'userId-index')
        response = list.list_main(api_gateway_event)
        body = json.loads(response['body'])

        assert len(body['owned']) == 1, "Number of lists returned was not as expected."
        assert len(body['shared']) == 2, "Number of lists returned was not as expected."

    def test_list_main_no_table(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'userId-index')
        response = list.list_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting lists from table.', "Exception was not as expected."

    def test_list_main_user_with_no_lists(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'userId-index')
        api_gateway_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"
        response = list.list_main(api_gateway_event)
        body = json.loads(response['body'])

        assert len(body['owned']) == 0, "Number of lists returned was not as expected."
        assert len(body['shared']) == 0, "Number of lists returned was not as expected."


def test_handler(api_gateway_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'INDEX_NAME', 'userId-index')
    response = list.handler(api_gateway_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"user": .*}', response['body'])
