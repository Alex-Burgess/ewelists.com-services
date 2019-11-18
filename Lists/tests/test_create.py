import pytest
import os
import re
import json
import copy
import boto3
from moto import mock_dynamodb2
from lists import create
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_event():
    """ Generates API GW Event"""

    event = fixtures.api_gateway_base_event()
    event['httpMethod'] = "POST"
    event['body'] = "{\n    \"title\": \"My Birthday List\",\n    \"description\": \"A gift wish list for my birthday.\",\n    \"occasion\": \"Birthday\",\n    \"imageUrl\": \"/images/celebration-default.jpg\"\n}"

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

    # 1 User, with 1 list.
    items = [
        {"PK": "USER#12345678-user-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "email": "test.user@gmail.com", "name": "Test User", "userId": "12345678-user-0001-1234-abcdefghijkl"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
    ]

    for item in items:
        table.put_item(TableName='lists-unittest', Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetAttributeDetails:
    def test_get_attribute_details(self, api_gateway_event):
        attribute_details = create.get_attribute_details(api_gateway_event)
        assert attribute_details['title'] == "My Birthday List", "Attribute title was not as expected."
        assert attribute_details['description'] == "A gift wish list for my birthday.", "Attribute description was not as expected."
        assert attribute_details['occasion'] == "Birthday", "Attribute occasion was not as expected."
        assert attribute_details['imageUrl'] == "/images/celebration-default.jpg", "Attribute imageUrl was not as expected."

    def test_get_attribute_details_with_empty_body(self, api_gateway_event):
        event_no_body = copy.deepcopy(api_gateway_event)
        event_no_body['body'] = None

        with pytest.raises(Exception) as e:
            create.get_attribute_details(event_no_body)
        assert str(e.value) == "API Event did not contain a valid body.", "Exception not as expected."


class TestGenerateListId:
    def test_generate_list_id(self):
        list_id = create.generate_list_id()
        assert len(list_id) == 36, "List ID not 36 characters long."
        assert list_id != '12345678-list-0001-1234-abcdefghijkl', "List ID shouldn't match the ID of the list already in the table (Pretty Unlikely)."


class TestPutItemInTable:
    def test_put_item_in_table(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0002-1234-abcdefghijkl'

        attributes = {
            'title': 'My Test List',
            'description': 'Test description for the list.',
            'occasion': 'Birthday',
            'imageUrl': '/images/celebration-default.jpg'
        }

        message = create.put_item_in_table('lists-unittest', user_id, list_id, attributes)
        assert message == "List was created.", "Put item message not as expected."

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.query(
            TableName='lists-unittest',
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        assert len(test_response['Items']) == 2, "Number of items for new list should be 2."
        assert test_response['Items'][0]['PK']['S'] == 'LIST#12345678-list-0002-1234-abcdefghijkl', "PK of item was not as expected."
        assert test_response['Items'][0]['imageUrl']['S'] == '/images/celebration-default.jpg', "imageurl of item was not as expected."

        assert test_response['Items'][1]['PK']['S'] == 'LIST#12345678-list-0002-1234-abcdefghijkl', "PK of item was not as expected."
        assert test_response['Items'][1]['imageUrl']['S'] == '/images/celebration-default.jpg', "imageurl of item was not as expected."

    def test_put_item_in_table_with_bad_name(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0002-1234-abcdefghijkl'

        attributes = {
            'title': 'My Test List',
            'description': 'Test description for the list.',
            'occasion': 'Birthday',
            'imageUrl': '/images/celebration-default.jpg'
        }

        with pytest.raises(Exception) as e:
            create.put_item_in_table('lists-unittes', user_id, list_id, attributes)
        assert str(e.value) == "List could not be created.", "Exception not as expected."


class TestCreateMain:
    def test_create_main(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = create.create_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['message'] == 'List was created.', "Create main response did not contain the correct message."
        assert len(body['listId']) == 36, "Create main response did not contain a listId."

    def test_create_main_with_no_event_body(self, monkeypatch, api_gateway_event, dynamodb_mock):
        event_no_body = copy.deepcopy(api_gateway_event)
        event_no_body['body'] = None
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = create.create_main(event_no_body)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event did not contain a valid body.', "Create main response did not contain the correct error message."


def test_handler(api_gateway_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = create.handler(api_gateway_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"listId": .*}', response['body'])
