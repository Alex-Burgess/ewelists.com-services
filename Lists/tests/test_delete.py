import os
import re
import pytest
import json
from lists import delete, logger

log = logger.setup_logger()


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

    def test_delete_item_no_list(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0009-1234-abcdefghijkl'
        items = [{
            "PK": {'S': "LIST#{}".format(list_id)},
            'SK': {'S': "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}
        }]

        with pytest.raises(Exception) as e:
            delete.delete_items('lists-unittest', user_id, list_id, items)
        assert str(e.value) == "List does not exist.", "Exception not as expected."


class TestGetItemsAssociatedWithList:
    def test_get_items_associated_with_list(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        items = delete.get_items_associated_with_list('lists-unittest', list_id)
        assert len(items) == 14, "Number of items deleted was not as expected."


class TestDeleteMain:
    def test_delete_main(self, api_delete_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = delete.delete_main(api_delete_event)
        body = json.loads(response['body'])

        assert body['deleted'], "Delete main response did not contain the correct status."
        assert len(body['listId']) == 36, "Create main response did not contain a listId."

    def test_delete_main_with_bad_table_name(self, api_delete_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = delete.delete_main(api_delete_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Unexpected error when getting list items from table.', "Create main response did not contain the correct error message."

    def test_delete_main_with_bad_user(self, api_delete_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_delete_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"
        response = delete.delete_main(api_delete_event)
        body = json.loads(response['body'])
        assert body['error'] == 'User 12345678-user-0003-1234-abcdefghijkl was not owner of List 12345678-list-0001-1234-abcdefghijkl.', "Create main response did not contain the correct error message."

    def test_delete_main_with_bad_list(self, api_delete_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_delete_event['pathParameters']['id'] = "12345678-list-0100-1234-abcdefghijkl"

        response = delete.delete_main(api_delete_event)
        body = json.loads(response['body'])
        assert body['error'] == 'User 12345678-user-0001-1234-abcdefghijkl was not owner of List 12345678-list-0100-1234-abcdefghijkl.', "Create main response did not contain the correct error message."


def test_handler(api_delete_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = delete.handler(api_delete_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    assert re.match('{"deleted": .*}', response['body']), "Response body was not as expected."

    body = json.loads(response['body'])
    assert body['count'] == 14, "Number of items deleted was not as expected."
