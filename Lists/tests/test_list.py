import pytest
import os
import re
import json
from lists import list, logger

log = logger.setup_test_logger()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'INDEX_NAME', 'userId-index')

    return monkeypatch


class TestGetLists:
    def test_get_lists_for_requestor(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        lists_response = list.get_lists('lists-unittest', 'userId-index', user_id)

        assert lists_response['user'] == {"email": "test.user1@gmail.com", "name": "Test User1", "userId": "12345678-user-0001-1234-abcdefghijkl"}, "Test user was not as expected."

        owned_list1 = {"listId": "12345678-list-0001-1234-abcdefghijkl", 'listOwner': '12345678-user-0001-1234-abcdefghijkl', "title": "Child User1 1st Birthday", "occasion": "Birthday", "description": "A gift list for Child User1 birthday.", "eventDate": "31 October 2018", "imageUrl": "/images/celebration-default.jpg", "state": "open"}
        owned_list2 = {"listId": "12345678-list-0002-1234-abcdefghijkl", 'listOwner': '12345678-user-0001-1234-abcdefghijkl', "title": "Child User1 Christmas List", "occasion": "Christmas", "description": "A gift list for Child User1 Christmas.", "imageUrl": "/images/christmas-default.jpg", "state": "open"}
        closed_list1 = {"listId": "12345678-list-0003-1234-abcdefghijkl", 'listOwner': '12345678-user-0001-1234-abcdefghijkl', "title": "Child 2 Christmas List", "occasion": "Christmas", "description": "A gift list for Child 2 Christmas.", "imageUrl": "/images/christmas-default.jpg", "state": "closed"}
        assert len(lists_response['owned']) == 2, "User should only own 1 list."
        assert lists_response['owned'][0] == owned_list1, "Details of the list owned by user was not as expected."
        assert lists_response['owned'][1] == owned_list2, "Details of the list owned by user was not as expected."
        assert lists_response['closed'][0] == closed_list1, "Details of closed list was not as expected."

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
        assert len(lists_response['closed']) == 0, "Number of lists was not 0."


class TestListMain:
    def test_list_main(self, api_list_event, env_vars, dynamodb_mock):
        response = list.list_main(api_list_event)
        body = json.loads(response['body'])

        assert len(body['owned']) == 2, "Number of lists returned was not as expected."
        assert len(body['closed']) == 1, "Number of closed lists returned was not as expected."

    def test_list_main_no_table(self, api_list_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'userId-index')
        response = list.list_main(api_list_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting lists from table.', "Exception was not as expected."

    def test_list_main_user_with_no_lists(self, api_list_event, env_vars, dynamodb_mock):
        api_list_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"
        response = list.list_main(api_list_event)
        body = json.loads(response['body'])

        assert len(body['owned']) == 0, "Number of lists returned was not as expected."
        assert len(body['closed']) == 0, "Number of lists was not 0."


def test_handler(api_list_event, env_vars, dynamodb_mock):
    response = list.handler(api_list_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"user": .*}', response['body'])
