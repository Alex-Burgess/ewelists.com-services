import pytest
import json
import boto3
from moto import mock_ses
from contact import contact_us

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_event():
    event = api_gateway_base_event()
    event['resource'] = "/contact"
    event['path'] = "/contact"
    event['httpMethod'] = "POST"
    event['body'] = "{\n    \"name\": \"Test User1\",\n    \"email\": \"test.user1@gmail.com\",\n    \"message\": \"A test message.\"\n}"

    return event


@pytest.fixture
def ses_mock():
    mock = mock_ses()
    mock.start()

    ses = boto3.client('ses', region_name='eu-west-1')
    ses.verify_email_identity(EmailAddress="contact@ewelists.com")

    yield
    # teardown: stop moto server
    mock.stop()


class TestContactMain:
    def test_contact_main(self, ses_mock, api_gateway_event):
        response = contact_us.contact_main(api_gateway_event)
        body = json.loads(response['body'])

        assert body['name'] == 'Test User1', "Attribute was not as expected."
        assert body['email'] == 'test.user1@gmail.com', "Attribute was not as expected."
        assert body['message'] == 'A test message.', "Attribute was not as expected."
        assert body['id'] > 100000
        assert body['id'] < 999999

    def test_body_missing(self, ses_mock, api_gateway_event):
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
    def test_send_email(self, ses_mock):
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


def api_gateway_base_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists",
        "path": "/lists",
        "httpMethod": "GET",
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "GB",
            "Content-Type": "text/plain",
            "Host": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "Postman-Token": "512388b6-c036-4d11-a6c9-adf8e07e1da0",
            "User-Agent": "PostmanRuntime/7.15.2",
            "Via": "1.1 a1cb6e97bccd4899987b343ae5d4c252.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "zJgUVrLX5O4d-B43SVe4Bs6YVpSTWXxrAVtWjeF0FcAnXJ8dARKQRA==",
            "x-amz-content-sha256": "b9d4c66e0ae3c09af8a6ce4c99518f244c3db701a196021c79f094b51e9b49d4",
            "x-amz-date": "20191008T162240Z",
            "X-Amzn-Trace-Id": "Root=1-5d9cb7d0-6965798907570a0728570212",
            "X-Forwarded-For": "5.81.150.55, 70.132.38.104",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "queryStringParameters": "null",
        "multiValueQueryStringParameters": "null",
        "pathParameters": "null",
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/lists",
            "httpMethod": "GET",
            "extendedRequestId": "BQGojGkBjoEFsTw=",
            "requestTime": "08/Oct/2019:16:22:40 +0000",
            "path": "/test/lists",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "test",
            "domainPrefix": "4sdcvv0n2e",
            "requestTimeEpoch": 1570551760227,
            "requestId": "a3d965cd-a79b-4249-867a-a03eb858a839",
            "identity": {
                "cognitoIdentityPoolId": "eu-west-1:2208d797-dfc9-40b4-8029-827c9e76e029",
                "accountId": "123456789012",
                "cognitoIdentityId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c",
                "caller": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials",
                "sourceIp": "31.49.230.217",
                "principalOrgId": "o-d8jj6dyqv2",
                "accessKey": "ABCDEFGPDMJL4EB35H6H",
                "cognitoAuthenticationType": "authenticated",
                "cognitoAuthenticationProvider": "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0001-1234-abcdefghijkl",
                "userArn": "arn:aws:sts::123456789012:assumed-role/Ewelists-test-CognitoAuthRole/CognitoIdentityCredentials",
                "userAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Mobile Safari/537.36",
                "user": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials"
            },
            "domainName": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "apiId": "4sdcvv0n2e"
        },
        "body": "null",
        "isBase64Encoded": "false"
    }
