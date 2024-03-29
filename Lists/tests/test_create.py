import pytest
import os
import re
import json
import copy
import boto3
from lists import create, logger

log = logger.setup_test_logger()


class TestGetAttributeDetails:
    def test_get_attribute_details(self, api_create_event):
        attribute_details = create.get_attribute_details(api_create_event)
        assert attribute_details['title'] == "My Birthday List", "Attribute title was not as expected."
        assert attribute_details['description'] == "A gift wish list for my birthday.", "Attribute description was not as expected."
        assert attribute_details['eventDate'] == "25 December 2020", "Attribute date was not as expected."
        assert attribute_details['occasion'] == "Birthday", "Attribute occasion was not as expected."
        assert attribute_details['imageUrl'] == "/images/celebration-default.jpg", "Attribute imageUrl was not as expected."

    def test_get_attribute_details_with_empty_body(self, api_create_event):
        event_no_body = copy.deepcopy(api_create_event)
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
        list_id = '12345678-list-0012-1234-abcdefghijkl'
        users_name = 'Test User1'

        attributes = {
            'title': 'My Test List',
            'description': 'Test description for the list.',
            'eventDate': '25 December 2020',
            'occasion': 'Birthday',
            'imageUrl': '/images/celebration-default.jpg'
        }

        assert create.put_item_in_table('lists-unittest', user_id, list_id, attributes, users_name)

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.query(
            TableName='lists-unittest',
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        assert len(test_response['Items']) == 1, "Number of items for new list should be 1."

        assert test_response['Items'][0]['PK']['S'] == 'LIST#12345678-list-0012-1234-abcdefghijkl', "Attribute of item was not as expected."
        assert test_response['Items'][0]['SK']['S'] == "USER#12345678-user-0001-1234-abcdefghijkl", "Attribute was not as expected."
        assert test_response['Items'][0]['userId']['S'] == "12345678-user-0001-1234-abcdefghijkl", "Attribute was not as expected."
        assert test_response['Items'][0]['title']['S'] == "My Test List", "Attribute was not as expected."
        assert test_response['Items'][0]['eventDate']['S'] == "25 December 2020", "Attribute was not as expected."
        assert test_response['Items'][0]['occasion']['S'] == "Birthday", "Attribute was not as expected."
        assert test_response['Items'][0]['listId']['S'] == "12345678-list-0012-1234-abcdefghijkl", "Attribute was not as expected."
        assert len(test_response['Items'][0]['createdAt']['N']) == 10, "Attribute was not as expected."
        assert test_response['Items'][0]['description']['S'] == "Test description for the list.", "Attribute was not as expected."
        assert test_response['Items'][0]['imageUrl']['S'] == '/images/celebration-default.jpg', "imageurl of item was not as expected."
        assert test_response['Items'][0]['state']['S'] == 'open', "Status of item was not as expected."

    def test_put_item_in_table_with_bad_name(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0012-1234-abcdefghijkl'
        users_name = 'Test User1'

        attributes = {
            'title': 'My Test List',
            'description': 'Test description for the list.',
            'occasion': 'Birthday',
            'imageUrl': '/images/celebration-default.jpg'
        }

        with pytest.raises(Exception) as e:
            create.put_item_in_table('lists-unittes', user_id, list_id, attributes, users_name)
        assert str(e.value) == "List could not be created.", "Exception not as expected."


class TestCreateMain:
    def test_create_main(self, monkeypatch, api_create_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = create.create_main(api_create_event)
        body = json.loads(response['body'])

        assert len(body['listId']) == 36, "Create main response did not contain a listId."

    def test_create_main_with_no_event_body(self, monkeypatch, api_create_event, dynamodb_mock):
        event_no_body = copy.deepcopy(api_create_event)
        event_no_body['body'] = None
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = create.create_main(event_no_body)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event did not contain a valid body.', "Create main response did not contain the correct error message."


def test_handler(api_create_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = create.handler(api_create_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"listId": .*}', response['body'])
