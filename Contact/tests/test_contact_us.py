import pytest
import json
from contact import contact_us
import sys
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestContactMain:
    def test_contact_main(self, ses, api_gateway_event):
        response = contact_us.contact_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['name'] == 'Test User1', "Attribute was not as expected."
        assert body['email'] == 'test.user1@gmail.com', "Attribute was not as expected."
        assert body['message'] == 'A test message.', "Attribute was not as expected."
        assert body['id'] > 100000
        assert body['id'] < 999999

    def test_body_missing(self, ses, api_gateway_event):
        api_gateway_event['body'] = None
        response = contact_us.contact_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['error'] == 'API Event did not contain name in the body.', "Error was not as expected."


class TestGetId:
    def test_get_id(self):
        id = contact_us.get_id()
        assert id > 100000
        assert id < 999999


class TestSendEmail:
    def test_send_email(self, ses):
        body = "<html><head></head><body><h3>Hi Test User2,</h3></body></html>"
        subject = "Ewemail from Test User. #123456"
        assert contact_us.send(body, subject)


class TestEmail:
    def test_email_html(self):
        name = "Test User1"
        email = "test.user1@gmail.com"
        message = "Can you help with an issue please."

        expected_html = "<html><head></head><body>Name: Test User1<br />Email: test.user1@gmail.com<br />Message:<p>Can you help with an issue please.</p></body></html>"

        assert contact_us.html_body(name, email, message) == expected_html, "Email html was not as expected."

    def test_get_subject(self):
        subject = contact_us.get_subject("Test User", 123456)
        assert subject == "Ewemail from Test User. #123456", "Subject not correct."


class TestGetSenderDetails:
    def test_get_users_name(self, api_gateway_event):
        assert contact_us.get_sender_details(api_gateway_event, 'name') == 'Test User1', "Attribute value was wrong."

    def test_get_users_email(self, api_gateway_event):
        assert contact_us.get_sender_details(api_gateway_event, 'email') == 'test.user1@gmail.com', "Attribute value was wrong."

    def test_get_users_message(self, api_gateway_event):
        assert contact_us.get_sender_details(api_gateway_event, 'message') == 'A test message.', "Attribute value was wrong."

    def test_get_missing_attribute(self, api_gateway_event):
        with pytest.raises(Exception) as e:
            contact_us.get_sender_details(api_gateway_event, 'unknown')
        assert str(e.value) == "API Event did not contain unknown in the body.", "Exception not as expected."


def test_create_response():
    response = contact_us.create_response(200, 'Success message')

    expected_response = {'statusCode': 200,
                         'body': 'Success message',
                         'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                         }}
    assert response == expected_response, "Create_response did not return the expected response value."
