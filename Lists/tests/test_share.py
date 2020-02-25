import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2, mock_ses
from lists import share
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_share_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/share/{user}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/share/test.user3%40gmail.com"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"user": "test.user3%40gmail.com", "id": "12345678-list-0001-1234-abcdefghijkl"}
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
        AttributeDefinitions=[{'AttributeName': 'PK', 'AttributeType': 'S'}, {'AttributeName': 'SK', 'AttributeType': 'S'}, {'AttributeName': 'email', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
        GlobalSecondaryIndexes=[{
            'IndexName': 'email-index',
            'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
            'Projection': {
                'ProjectionType': 'ALL'
            }
        }]
    )

    items = fixtures.load_test_data()

    for item in items:
        table.put_item(TableName='lists-unittest', Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


@pytest.fixture
def ses_mock():
    mock = mock_ses()
    mock.start()

    ses = boto3.client('ses', region_name='eu-west-1')
    ses.verify_email_identity(EmailAddress="contact@ewelists.com")

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetUserIfExists:
    def test_get_user_if_exists(self, dynamodb_mock):
        email = 'test.user3@gmail.com'
        user = share.get_user_if_exists('lists-unittest', 'email-index', email)
        expected_item = {"email": "test.user3@gmail.com", "name": "Test User3", "userId": "12345678-user-0003-1234-abcdefghijkl"}

        assert user == expected_item, "User item was not as expected."

    def test_user_does_not_exist(self, dynamodb_mock):
        email = 'test.user30@gmail.com'
        user = share.get_user_if_exists('lists-unittest', 'email-index', email)
        assert len(user) == 0, "User object was not empty."

    def test_with_bad_index(self, dynamodb_mock):
        email = 'test.user30@gmail.com'
        with pytest.raises(Exception) as e:
            share.get_user_if_exists('lists-unittest', 'email-inde', email)
        assert str(e.value) == "Unexpected error when getting user from table.", "Exception not as expected."


class TestCreateSharedEntry:
    def test_create_shared_entry(self, dynamodb_mock):
        user = {"email": "test.user3@gmail.com", "name": "Test User3", "userId": "12345678-user-0003-1234-abcdefghijkl"}
        list_item = {
            'listId': {'S': "12345678-list-0001-1234-abcdefghijkl"},
            'title': {'S': "Child User1 1st Birthday"},
            'description': {'S': "A gift list for Child User1 birthday."},
            'eventDate': {'S': "31 October 2018"},
            'occasion': {'S': "Birthday"},
            'imageUrl': {'S': "/images/celebration-default.jpg"},
            'listOwner': {'S': "12345678-user-0001-1234-abcdefghijkl"}
        }

        assert share.create_shared_entry('lists-unittest', user, list_item)

    def test_attempt_to_create_duplicate(self, dynamodb_mock):
        user = {"email": "test.user1@gmail.com", "name": "Test User1", "userId": "12345678-user-0001-1234-abcdefghijkl"}
        list_item = {
            'listId': {'S': "12345678-list-0001-1234-abcdefghijkl"},
            'title': {'S': "Child User1 1st Birthday"},
            'description': {'S': "A gift list for Child User1 birthday."},
            'eventDate': {'S': "31 October 2018"},
            'occasion': {'S': "Birthday"},
            'imageUrl': {'S': "/images/celebration-default.jpg"},
            'listOwner': {'S': "12345678-user-0001-1234-abcdefghijkl"}
        }

        with pytest.raises(Exception) as e:
            share.create_shared_entry('lists-unittest', user, list_item)
        assert str(e.value) == "User already exists in list.", "Exception not as expected."


class TestCreatePendingEntry:
    def test_create_pending_entry(self, dynamodb_mock):
        email = "test.user30@gmail.com"
        list_item = {
            'listId': {'S': "12345678-list-0001-1234-abcdefghijkl"},
            'title': {'S': "Child User1 1st Birthday"},
            'description': {'S': "A gift list for Child User1 birthday."},
            'eventDate': {'S': "31 October 2018"},
            'occasion': {'S': "Birthday"},
            'imageUrl': {'S': "/images/celebration-default.jpg"},
            'listOwner': {'S': "12345678-user-0001-1234-abcdefghijkl"}
        }

        assert share.create_pending_entry('lists-unittest', email, list_item)

    def test_attempt_to_create_duplicate(self, dynamodb_mock):
        email = "test.user4@gmail.com"
        list_item = {
            'listId': {'S': "12345678-list-0001-1234-abcdefghijkl"},
            'title': {'S': "Child User1 1st Birthday"},
            'description': {'S': "A gift list for Child User1 birthday."},
            'eventDate': {'S': "31 October 2018"},
            'occasion': {'S': "Birthday"},
            'imageUrl': {'S': "/images/celebration-default.jpg"},
            'listOwner': {'S': "12345678-user-0001-1234-abcdefghijkl"}
        }

        with pytest.raises(Exception) as e:
            share.create_pending_entry('lists-unittest', email, list_item)
        assert str(e.value) == "User already exists in list.", "Exception not as expected."


class TestEmailSubject:
    def tets_email_subject(self):
        list_owner_name = "Alex Burgess"
        assert share.email_subject(list_owner_name) == "Alex Burgess shared a gift list with you!", "Subject was not as expected."


class TestExistsUrl:
    def exist_url(self):
        list_id = "12345678-list-0001-1234-abcdefghijkl"
        url = "https://test.ewelists.com"
        assert share.list_url(url, list_id) == "https://test.ewelists.com/lists/12345678-list-0001-1234-abcdefghijkl", "url is not as expected."


class TestSignupUrl:
    def exist_url(self):
        list_id = "12345678-list-0001-1234-abcdefghijkl"
        url = "https://test.ewelists.com"
        assert share.list_url(url, list_id) == "https://test.ewelists.com/signup?redirect=/lists/12345678-list-0001-1234-abcdefghijkl", "url is not as expected."


class TestPendingEmailText:
    def test_pending_email_text(self):
        list_owner_name = "Test User1"
        list_title = "Test 1st Birthday List"
        url = "https://test.ewelists.com/lists/12345678-list-0001-1234-abcdefghijkl"

        expected_text = "Hi,\r\nTest User1 shared Test 1st Birthday List with you on Ewelists.\r\nYou can view this list by signing up at https://test.ewelists.com/lists/12345678-list-0001-1234-abcdefghijkl"
        assert share.pending_email_text(list_owner_name, list_title, url) == expected_text, "Email text was not as expected."


class TestPendingEmailHtml:
    def test_pending_email_html(self):
        list_owner_name = "Test User1"
        list_title = "Test 1st Birthday List"
        url = "https://test.ewelists.com/lists/12345678-list-0001-1234-abcdefghijkl"

        expected_html = "<html><head></head><body><p>Hi,</p><p>Test User1 shared Test 1st Birthday List with you on Ewelists.</p>You can view this list by signing up at <a href=\"https://test.ewelists.com/lists/12345678-list-0001-1234-abcdefghijkl\">Ewelists</a></body></html>"

        assert share.pending_email_html(list_owner_name, list_title, url) == expected_html, "Email html was not as expected."


class TestSharedEmailText:
    def test_shared_email_text(self):
        recipient_name = "Test User2"
        list_owner_name = "Test User1"
        list_title = "Test 1st Birthday List"
        url = "https://test.ewelists.com/lists/12345678-list-0001-1234-abcdefghijkl"

        expected_text = "Hi Test User2,\r\nTest User1 shared Test 1st Birthday List with you on Ewelists.\r\nYou can view this list by signing up at https://test.ewelists.com/lists/12345678-list-0001-1234-abcdefghijkl"
        assert share.shared_email_text(recipient_name, list_owner_name, list_title, url) == expected_text, "Email text was not as expected."


class TestSharedEmailHtml:
    def test_shared_email_html(self):
        recipient_name = "Test User2"
        list_owner_name = "Test User1"
        list_title = "Test 1st Birthday List"
        url = "https://test.ewelists.com/lists/12345678-list-0001-1234-abcdefghijkl"

        expected_html = "<html><head></head><body><h3>Hi Test User2,</h3><p>Test User1 shared Test 1st Birthday List with you on Ewelists.</p><a href=\"https://test.ewelists.com/lists/12345678-list-0001-1234-abcdefghijkl\">View List</a></body></html>"

        assert share.shared_email_html(recipient_name, list_owner_name, list_title, url) == expected_html, "Email html was not as expected."


class TestSendEmail:
    def test_send_email(self, ses_mock):
        recipient = "success@simulator.amazonses.com"
        body_text = "Amazon SES Test (Python)\r\nThis email was sent with Amazon SES using the AWS SDK for Python (Boto)."
        body_html = "<html><head></head><body><h3>Hi Test User2,</h3></body></html>"
        subject = "Test subject"

        assert share.send_email(recipient, body_text, body_html, subject)


class TestShareMain:
    def test_share_when_user_exists(self, ses_mock, dynamodb_mock, monkeypatch, api_gateway_share_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
        response = share.share_main(api_gateway_share_event)
        body = json.loads(response['body'])

        assert body['user']['userId'] == '12345678-user-0003-1234-abcdefghijkl', "User attribute was not as expected."
        assert body['user']['email'] == 'test.user3@gmail.com', "User attribute was not as expected."
        assert body['user']['name'] == 'Test User3', "User attribute was not as expected."
        assert body['user']['type'] == 'SHARED', "User attribute was not as expected."

        # Check that shared entry created in table
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#12345678-list-0001-1234-abcdefghijkl"}, 'SK': {'S': "SHARED#12345678-user-0003-1234-abcdefghijkl"}}
        )

        assert test_response['Item']['PK']['S'] == 'LIST#12345678-list-0001-1234-abcdefghijkl', "Item attribute not as expected."
        assert test_response['Item']['SK']['S'] == 'SHARED#12345678-user-0003-1234-abcdefghijkl', "Item attribute not as expected."
        assert test_response['Item']['listId']['S'] == '12345678-list-0001-1234-abcdefghijkl', "Item attribute not as expected."
        assert test_response['Item']['listOwner']['S'] == '12345678-user-0001-1234-abcdefghijkl', "Item attribute not as expected."
        assert test_response['Item']['userId']['S'] == '12345678-user-0003-1234-abcdefghijkl', "Item attribute not as expected."
        assert test_response['Item']['shared_user_name']['S'] == 'Test User3', "Item attribute not as expected."
        assert test_response['Item']['shared_user_email']['S'] == 'test.user3@gmail.com', "Item attribute not as expected."
        assert test_response['Item']['title']['S'] == 'Child User1 1st Birthday', "Item attribute not as expected."
        assert test_response['Item']['occasion']['S'] == 'Birthday', "Item attribute not as expected."
        assert test_response['Item']['description']['S'] == 'A gift list for Child User1 birthday.', "Item attribute not as expected."
        assert test_response['Item']['imageUrl']['S'] == '/images/celebration-default.jpg', "Item attribute not as expected."

    def test_share_when_user_does_not_exist(self, ses_mock, dynamodb_mock, monkeypatch, api_gateway_share_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
        api_gateway_share_event['pathParameters']['user'] = 'test.user20@gmail.com'

        response = share.share_main(api_gateway_share_event)
        body = json.loads(response['body'])

        assert body['user']['email'] == 'test.user20@gmail.com', "User attribute was not as expected."
        assert body['user']['type'] == 'PENDING', "User attribute was not as expected."

        # Check that shared entry created in table
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#12345678-list-0001-1234-abcdefghijkl"}, 'SK': {'S': "PENDING#test.user20@gmail.com"}}
        )

        assert test_response['Item']['PK']['S'] == 'LIST#12345678-list-0001-1234-abcdefghijkl', "Item attribute not as expected."
        assert test_response['Item']['SK']['S'] == 'PENDING#test.user20@gmail.com', "Item attribute not as expected."
        assert test_response['Item']['listId']['S'] == '12345678-list-0001-1234-abcdefghijkl', "Item attribute not as expected."
        assert test_response['Item']['listOwner']['S'] == '12345678-user-0001-1234-abcdefghijkl', "Item attribute not as expected."
        assert test_response['Item']['shared_user_email']['S'] == 'test.user20@gmail.com', "Item attribute not as expected."
        assert test_response['Item']['title']['S'] == 'Child User1 1st Birthday', "Item attribute not as expected."
        assert test_response['Item']['occasion']['S'] == 'Birthday', "Item attribute not as expected."
        assert test_response['Item']['description']['S'] == 'A gift list for Child User1 birthday.', "Item attribute not as expected."
        assert test_response['Item']['imageUrl']['S'] == '/images/celebration-default.jpg', "Item attribute not as expected."

    def test_share_with_email_with_spaces_and_capitals(self, ses_mock, dynamodb_mock, monkeypatch, api_gateway_share_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
        api_gateway_share_event['pathParameters'] = {"user": " Test.user3%40gmail.com ", "id": "12345678-list-0001-1234-abcdefghijkl"}
        response = share.share_main(api_gateway_share_event)
        body = json.loads(response['body'])

        assert body['user']['userId'] == '12345678-user-0003-1234-abcdefghijkl', "User attribute was not as expected."
        assert body['user']['email'] == 'test.user3@gmail.com', "User attribute was not as expected."
        assert body['user']['name'] == 'Test User3', "User attribute was not as expected."
        assert body['user']['type'] == 'SHARED', "User attribute was not as expected."

    def test_share_with_googlemail_dot_com_email(self, ses_mock, dynamodb_mock, monkeypatch, api_gateway_share_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
        api_gateway_share_event['pathParameters'] = {"user": "test.user3%40googlemail.com ", "id": "12345678-list-0001-1234-abcdefghijkl"}
        response = share.share_main(api_gateway_share_event)
        body = json.loads(response['body'])

        assert body['user']['userId'] == '12345678-user-0003-1234-abcdefghijkl', "User attribute was not as expected."
        assert body['user']['email'] == 'test.user3@gmail.com', "User attribute was not as expected."
        assert body['user']['name'] == 'Test User3', "User attribute was not as expected."
        assert body['user']['type'] == 'SHARED', "User attribute was not as expected."

    def test_requestor_is_not_list_owner(self, ses_mock, dynamodb_mock, monkeypatch, api_gateway_share_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
        user = '12345678-user-0010-1234-abcdefghijkl'
        api_gateway_share_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:" + user

        response = share.share_main(api_gateway_share_event)
        body = json.loads(response['body'])

        assert body['error'] == 'No list exists with this ID.', "Error was not as expected."

    def test_list_does_not_exist(self, ses_mock, dynamodb_mock, monkeypatch, api_gateway_share_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
        api_gateway_share_event['pathParameters']['id'] = "12345678-list-0020-1234-abcdefghijkl"

        response = share.share_main(api_gateway_share_event)
        body = json.loads(response['body'])

        assert body['error'] == 'No list exists with this ID.', "Error was not as expected."

    def test_empty_list_in_event(self, ses_mock, dynamodb_mock, monkeypatch, api_gateway_share_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
        api_gateway_share_event['pathParameters']['id'] = None

        response = share.share_main(api_gateway_share_event)
        body = json.loads(response['body'])

        assert body['error'] == 'API Event did not contain a List ID in the path parameters.', "Error was not as expected."

    def test_empty_user_in_event(self, ses_mock, dynamodb_mock, monkeypatch, api_gateway_share_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
        api_gateway_share_event['pathParameters']['user'] = 'null'

        response = share.share_main(api_gateway_share_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Path contained a null user parameter.', "Error was not as expected."


def test_handler(api_gateway_share_event, monkeypatch, ses_mock, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
    response = share.handler(api_gateway_share_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"user": .*}', response['body'])
