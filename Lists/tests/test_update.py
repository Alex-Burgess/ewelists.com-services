import pytest
import os
import json
from lists import update, logger

log = logger.setup_test_logger()


class TestGetAttributeDetails:
    def test_get_attribute_details_with_correct_attributes(self, api_update_event):
        update_attributes = update.get_attribute_details(api_update_event)

        assert len(update_attributes) == 5, "Update attributes object did not contain expected number of attributes."
        assert update_attributes['title'] == "My Updated Title", "Update attributes object did not contain title as expected."
        assert update_attributes['description'] == "Updated description for the list.", "Update attributes object did not contain description as expected."
        assert update_attributes['eventDate'] == "25 December 2020", "Update attributes object did not contain date as expected."
        assert update_attributes['occasion'] == "Christmas", "Update attributes object did not contain occasion as expected."
        assert update_attributes['imageUrl'] == "/images/christmas-default.jpg", "Update attributes object did not contain imageUrl as expected."

    def test_get_attribute_details_with_one_attributes(self, api_update_event):
        api_update_event['body'] = "{\n    \"title\": \"My Updated Title\"\n}"

        with pytest.raises(Exception) as e:
            update.get_attribute_details(api_update_event)
        assert str(e.value) == "Event body did not contain the expected keys ['title', 'description', 'eventDate', 'occasion', 'imageUrl'].", "Exception not as expected."

    def test_get_attribute_details_with_empty_body(self, api_update_event):
        api_update_event['body'] = None

        with pytest.raises(Exception) as e:
            update.get_attribute_details(api_update_event)
        assert str(e.value) == "API Event did not contain a valid body.", "Exception not as expected."

    def test_get_attribute_details_with_body_not_json(self, api_update_event):
        api_update_event['body'] = "some text"

        with pytest.raises(Exception) as e:
            update.get_attribute_details(api_update_event)
        assert str(e.value) == "API Event did not contain a valid body.", "Exception not as expected."


class TestGetItemsToUpdate:
    def test_get_items_to_update(self, dynamodb_mock):
        items = update.get_items_to_update('lists-unittest', '12345678-list-0001-1234-abcdefghijkl')
        assert len(items) == 1
        assert items[0]['SK']['S'] == 'USER#12345678-user-0001-1234-abcdefghijkl'


class TestUpdateList:
    def test_update_list_title(self, api_update_event, dynamodb_mock):
        api_update_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"A gift list for Child User1 birthday.\",\n    \"eventDate\": \"31 October 2018\",\n    \"occasion\": \"Birthday\",\n    \"imageUrl\": \"/images/celebration-default.jpg\"\n}"
        update_attributes = json.loads(api_update_event['body'])
        items = [
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}}
        ]

        updates = update.update_list('lists-unittest', items, update_attributes)

        assert len(updates) == 1, "Update response did not contain expected number of updated attributes."
        assert updates[0]['SK'] == 'USER#12345678-user-0001-1234-abcdefghijkl'
        assert updates[0]['updates'] == {'title': 'My Updated Title'}

    def test_update_list_title_description_date_occasion(self, api_update_event, dynamodb_mock):
        api_update_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"Updated.\",\n    \"eventDate\": \"25 December 2025\",\n    \"occasion\": \"Christmas\",\n    \"imageUrl\": \"/images/christmas-default.jpg\"\n}"
        update_attributes = json.loads(api_update_event['body'])
        items = [
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '25 December 2025'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}}
        ]

        updates = update.update_list('lists-unittest', items, update_attributes)

        assert len(updates) == 1, "Update response did not contain expected number of updated attributes."
        assert updates[0]['SK'] == 'USER#12345678-user-0001-1234-abcdefghijkl'
        assert updates[0]['updates'] == {'title': 'My Updated Title', 'description': 'Updated.', 'eventDate': '25 December 2025', 'occasion': 'Christmas', 'imageUrl': '/images/christmas-default.jpg'}

    def test_update_list_removing_date(self, api_update_event, dynamodb_mock):
        api_update_event['body'] = "{\n    \"title\": \"Child User1 1st Birthday\",\n    \"description\": \"A gift list for Child User1 birthday.\",\n    \"eventDate\": \"\",\n    \"occasion\": \"Birthday\",\n    \"imageUrl\": \"/images/celebration-default.jpg\"\n}"
        update_attributes = json.loads(api_update_event['body'])
        items = [
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}}
        ]

        updates = update.update_list('lists-unittest', items, update_attributes)

        assert len(updates) == 1, "Update response did not contain expected number of updated attributes."
        assert updates[0]['SK'] == 'USER#12345678-user-0001-1234-abcdefghijkl'
        assert updates[0]['updates'] == {'eventDate': 'None'}


class TestUpdateListMain:
    def test_update_list_main_with_just_title(self, api_update_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_update_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"A gift list for Child User1 birthday.\",\n    \"eventDate\": \"31 October 2018\",\n    \"occasion\": \"Birthday\",\n    \"imageUrl\": \"/images/celebration-default.jpg\"\n}"
        response = update.update_list_main(api_update_event)
        body = json.loads(response['body'])

        expected_body = [
            {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "updates": {"title": "My Updated Title"}}
        ]

        assert len(body) == 1, "Update main response did not contain expected number of updated items."
        assert body == expected_body, "Updates from response were not as expected."

    def test_update_list_main_with_empty_body(self, monkeypatch, api_update_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_update_event['body'] = None
        response = update.update_list_main(api_update_event)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event did not contain a valid body.', "Update main response did not contain the correct error message."

    def test_update_list_that_does_not_exist(self, monkeypatch, api_update_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_update_event['pathParameters']['id'] = "12345678-list-0009-1234-abcdefghijkl"

        response = update.update_list_main(api_update_event)
        body = json.loads(response['body'])
        assert body['error'] == 'List 12345678-list-0009-1234-abcdefghijkl does not exist.', "Update main response did not contain the correct error message."

    def test_update_list_with_bad_table(self, monkeypatch, api_update_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')
        api_update_event['pathParameters']['id'] = "12345678-list-0009-1234-abcdefghijkl"

        response = update.update_list_main(api_update_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Unexpected error when getting list items from table.', "Update main response did not contain the correct error message."

    def test_update_list_with_requestor_not_owner(self, monkeypatch, api_update_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_update_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0002-1234-abcdefghijkl"

        response = update.update_list_main(api_update_event)
        body = json.loads(response['body'])
        assert body['error'] == 'User 12345678-user-0002-1234-abcdefghijkl was not owner of List 12345678-list-0001-1234-abcdefghijkl.', "Update main response did not contain the correct error message."


def test_handler(api_update_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = update.handler(api_update_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    expected_body = [
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "updates": {"title": "My Updated Title", "occasion": "Christmas", "description": "Updated description for the list.", "eventDate": "25 December 2020", "imageUrl": "/images/christmas-default.jpg"}}
    ]

    assert body == expected_body
