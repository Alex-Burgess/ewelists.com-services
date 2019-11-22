import pytest
import os
import json
import boto3
from moto import mock_dynamodb2
from lists import update
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
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl"
    event['httpMethod'] = "PUT"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"Updated description for the list.\",\n    \"eventDate\": \"25 December 2020\",\n    \"occasion\": \"Christmas\",\n    \"imageUrl\": \"/images/christmas-default.jpg\"\n}"

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


class TestGetAttributeDetails:
    def test_get_attribute_details_with_correct_attributes(self, api_gateway_event):
        update_attributes = update.get_attribute_details(api_gateway_event)

        assert len(update_attributes) == 5, "Update attributes object did not contain expected number of attributes."
        assert update_attributes['title'] == "My Updated Title", "Update attributes object did not contain title as expected."
        assert update_attributes['description'] == "Updated description for the list.", "Update attributes object did not contain description as expected."
        assert update_attributes['eventDate'] == "25 December 2020", "Update attributes object did not contain date as expected."
        assert update_attributes['occasion'] == "Christmas", "Update attributes object did not contain occasion as expected."
        assert update_attributes['imageUrl'] == "/images/christmas-default.jpg", "Update attributes object did not contain imageUrl as expected."

    def test_get_attribute_details_with_one_attributes(self, api_gateway_event):
        api_gateway_event['body'] = "{\n    \"title\": \"My Updated Title\"\n}"

        with pytest.raises(Exception) as e:
            update.get_attribute_details(api_gateway_event)
        assert str(e.value) == "Event body did not contain the expected keys ['title', 'description', 'eventDate', 'occasion', 'imageUrl'].", "Exception not as expected."

    def test_get_attribute_details_with_empty_body(self, api_gateway_event):
        api_gateway_event['body'] = "null"

        with pytest.raises(Exception) as e:
            update.get_attribute_details(api_gateway_event)
        assert str(e.value) == "API Event Body was empty.", "Exception not as expected."

    def test_get_attribute_details_with_body_not_json(self, api_gateway_event):
        api_gateway_event['body'] = "some text"

        with pytest.raises(Exception) as e:
            update.get_attribute_details(api_gateway_event)
        assert str(e.value) == "API Event did not contain a valid body.", "Exception not as expected."


class TestGetItemsToUpdate:
    def test_get_items_to_update(self, dynamodb_mock):
        items = update.get_items_to_update('lists-unittest', '12345678-list-0001-1234-abcdefghijkl')
        assert len(items) == 4
        assert items[0]['SK']['S'] == 'PENDING#test.user4@gmail.com'
        assert items[1]['SK']['S'] == 'SHARED#12345678-user-0001-1234-abcdefghijkl'
        assert items[2]['SK']['S'] == 'SHARED#12345678-user-0002-1234-abcdefghijkl'
        assert items[3]['SK']['S'] == 'USER#12345678-user-0001-1234-abcdefghijkl'


class TestUpdateList:
    def test_update_list_title(self, api_gateway_event, dynamodb_mock):
        api_gateway_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"A gift list for Child User1 birthday.\",\n    \"eventDate\": \"31 October 2018\",\n    \"occasion\": \"Birthday\",\n    \"imageUrl\": \"/images/celebration-default.jpg\"\n}"
        update_attributes = json.loads(api_gateway_event['body'])
        items = [
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'SHARED#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'shared_user_name': {'S': 'Test User 1'}, 'shared_user_email': {'S': 'test.user1@gmail.com'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}}
        ]

        updates = update.update_list('lists-unittest', items, update_attributes)

        assert len(updates) == 2, "Update response did not contain expected number of updated attributes."
        assert updates[0]['SK'] == 'SHARED#12345678-user-0001-1234-abcdefghijkl'
        assert updates[0]['updates'] == {'title': 'My Updated Title'}
        assert updates[1]['SK'] == 'USER#12345678-user-0001-1234-abcdefghijkl'
        assert updates[1]['updates'] == {'title': 'My Updated Title'}

    def test_update_list_title_description_date_occasion(self, api_gateway_event, dynamodb_mock):
        api_gateway_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"Updated.\",\n    \"eventDate\": \"25 December 2025\",\n    \"occasion\": \"Christmas\",\n    \"imageUrl\": \"/images/christmas-default.jpg\"\n}"
        update_attributes = json.loads(api_gateway_event['body'])
        items = [
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'SHARED#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '25 December 2025'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '25 December 2025'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}}
        ]

        updates = update.update_list('lists-unittest', items, update_attributes)

        assert len(updates) == 2, "Update response did not contain expected number of updated attributes."
        assert updates[0]['SK'] == 'SHARED#12345678-user-0001-1234-abcdefghijkl'
        assert updates[0]['updates'] == {'title': 'My Updated Title', 'description': 'Updated.', 'eventDate': '25 December 2025', 'occasion': 'Christmas', 'imageUrl': '/images/christmas-default.jpg'}
        assert updates[1]['SK'] == 'USER#12345678-user-0001-1234-abcdefghijkl'
        assert updates[1]['updates'] == {'title': 'My Updated Title', 'description': 'Updated.', 'eventDate': '25 December 2025', 'occasion': 'Christmas', 'imageUrl': '/images/christmas-default.jpg'}

    def test_update_list_removing_date(self, api_gateway_event, dynamodb_mock):
        api_gateway_event['body'] = "{\n    \"title\": \"Child User1 1st Birthday\",\n    \"description\": \"A gift list for Child User1 birthday.\",\n    \"eventDate\": \"\",\n    \"occasion\": \"Birthday\",\n    \"imageUrl\": \"/images/celebration-default.jpg\"\n}"
        update_attributes = json.loads(api_gateway_event['body'])
        items = [
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'SHARED#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}}
        ]

        updates = update.update_list('lists-unittest', items, update_attributes)

        assert len(updates) == 2, "Update response did not contain expected number of updated attributes."
        assert updates[0]['SK'] == 'SHARED#12345678-user-0001-1234-abcdefghijkl'
        assert updates[0]['updates'] == {'eventDate': 'None'}
        assert updates[1]['SK'] == 'USER#12345678-user-0001-1234-abcdefghijkl'
        assert updates[1]['updates'] == {'eventDate': 'None'}


class TestUpdateListMain:
    def test_update_list_main_with_just_title(self, api_gateway_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"A gift list for Child User1 birthday.\",\n    \"eventDate\": \"31 October 2018\",\n    \"occasion\": \"Birthday\",\n    \"imageUrl\": \"/images/celebration-default.jpg\"\n}"
        response = update.update_list_main(api_gateway_event)
        body = json.loads(response['body'])

        expected_body = [
            {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PENDING#test.user4@gmail.com", "updates": {"title": "My Updated Title"}},
            {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARED#12345678-user-0001-1234-abcdefghijkl", "updates": {"title": "My Updated Title"}},
            {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARED#12345678-user-0002-1234-abcdefghijkl", "updates": {"title": "My Updated Title"}},
            {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "updates": {"title": "My Updated Title"}}
        ]

        assert len(body) == 4, "Update main response did not contain expected number of updated items."
        assert body == expected_body, "Updates from response were not as expected."

    def test_update_list_main_with_empty_body(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['body'] = "null"
        response = update.update_list_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event Body was empty.', "Update main response did not contain the correct error message."

    def test_update_list_that_does_not_exist(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters']['id'] = "12345678-list-0009-1234-abcdefghijkl"

        response = update.update_list_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == 'No list exists with this ID.', "Update main response did not contain the correct error message."

    def test_update_list_with_bad_table(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')
        api_gateway_event['pathParameters']['id'] = "12345678-list-0009-1234-abcdefghijkl"

        response = update.update_list_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Unexpected error when getting lists from table.', "Update main response did not contain the correct error message."

    def test_update_list_with_requestor_not_owner(self, monkeypatch, api_gateway_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0002-1234-abcdefghijkl"

        response = update.update_list_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Owner of List ID 12345678-list-0001-1234-abcdefghijkl did not match user id of requestor: 12345678-user-0002-1234-abcdefghijkl.', "Update main response did not contain the correct error message."


def test_handler(api_gateway_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = update.handler(api_gateway_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    expected_body = [
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PENDING#test.user4@gmail.com", "updates": {"title": "My Updated Title", "occasion": "Christmas", "description": "Updated description for the list.", "eventDate": "25 December 2020", "imageUrl": "/images/christmas-default.jpg"}},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARED#12345678-user-0001-1234-abcdefghijkl", "updates": {"title": "My Updated Title", "occasion": "Christmas", "description": "Updated description for the list.", "eventDate": "25 December 2020", "imageUrl": "/images/christmas-default.jpg"}},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARED#12345678-user-0002-1234-abcdefghijkl", "updates": {"title": "My Updated Title", "occasion": "Christmas", "description": "Updated description for the list.", "eventDate": "25 December 2020", "imageUrl": "/images/christmas-default.jpg"}},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "updates": {"title": "My Updated Title", "occasion": "Christmas", "description": "Updated description for the list.", "eventDate": "25 December 2020", "imageUrl": "/images/christmas-default.jpg"}}
    ]

    assert body == expected_body
