import pytest
import os
from notfound import common
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_with_id_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/notfound/{id}"
    event['path'] = "/notfound/12345678-notf-0010-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-notf-0010-1234-abcdefghijkl"}
    event['body'] = "null"

    return event


@pytest.fixture
def api_gateway_postman_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/notfound/{id}"
    event['path'] = "/notfound/12345678-notf-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-notf-0001-1234-abcdefghijkl"}
    event['body'] = "null"

    event['requestContext']['identity'] = {
        "cognitoIdentityPoolId": "null",
        "accountId": "123456789012",
        "cognitoIdentityId": "null",
        "caller": "ABCDEFGPDMJL4EB35H6H",
        "sourceIp": "5.81.150.55",
        "principalOrgId": "o-d8jj6dyqv2",
        "accessKey": "ABCDEFGPDMJL4EB35H6H",
        "cognitoAuthenticationType": "null",
        "cognitoAuthenticationProvider": "null",
        "userArn": "arn:aws:iam::123456789012:user/ApiTestUser",
        "userAgent": "PostmanRuntime/7.15.2",
        "user": "ABCDEFGPDMJL4EB35H6H"
    }

    return event


@pytest.fixture
def api_gateway_event_with_no_identity():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/notfound/{id}"
    event['path'] = "/notfound/12345678-notf-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-notf-0001-1234-abcdefghijkl"}
    event['body'] = "null"
    event['requestContext']['identity'] = {}

    return event


@pytest.fixture
def api_gateway_event_with_no_product_id():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/notfound"
    event['path'] = "/notfound"
    event['httpMethod'] = "GET"

    return event


def test_create_response():
    response = common.create_response(200, 'Success message')

    expected_response = {'statusCode': 200,
                         'body': 'Success message',
                         'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                         }}
    assert response == expected_response, "Create_response did not return the expected response value."


class TestGetPostmanIdentity:
    def test_get_postman_identity(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')

        identity = common.get_postman_identity(os.environ, 1)
        assert identity == '12345678-user-api1-1234-abcdefghijkl', "POSTMAN_USERPOOL_SUB not as expected."

    def test_get_postman_identity2(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB2', '12345678-user-api2-1234-abcdefghijkl')

        identity = common.get_postman_identity(os.environ, 2)
        assert identity == '12345678-user-api2-1234-abcdefghijkl', "POSTMAN_USERPOOL_SUB2 not as expected."

    def test_get_postman_identity_when_identity_id_missing(self):
        with pytest.raises(Exception) as e:
            common.get_postman_identity(os.environ, 1)
        assert str(e.value) == "POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."


class TestGetIdentity:
    def test_get_identity(self, api_gateway_with_id_event):
        identity = common.get_identity(api_gateway_with_id_event, os.environ)
        assert identity == "12345678-user-0001-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_postman_request(self, monkeypatch, api_gateway_postman_event):
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')
        identity = common.get_identity(api_gateway_postman_event, os.environ)
        assert identity == "12345678-user-api1-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_postman2_request(self, monkeypatch, api_gateway_postman_event):
        api_gateway_postman_event['requestContext']['identity']['userArn'] = "arn:aws:iam::123456789012:user/ApiTestUser2"
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB2', '12345678-user-api2-1234-abcdefghijkl')
        identity = common.get_identity(api_gateway_postman_event, os.environ)
        assert identity == "12345678-user-api2-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_noid(self, api_gateway_event_with_no_identity):
        with pytest.raises(Exception) as e:
            common.get_identity(api_gateway_event_with_no_identity, os.environ)
        assert str(e.value) == "There was no identity context in API event.", "Exception not as expected."

    def test_get_identity_when_postman_request_and_with_no_osvars(self, api_gateway_postman_event):
        with pytest.raises(Exception) as e:
            common.get_identity(api_gateway_postman_event, os.environ)
        assert str(e.value) == "POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."


class TestGetTableName:
    def test_get_table_name(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-test')
        table_name = common.get_table_name(os.environ)
        assert table_name == "notfound-test", "Table name from os environment variables was not as expected."

    def test_get_table_name_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_table_name(os.environ)
        assert str(e.value) == "TABLE_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetProductId:
    def test_get_product_id(self, api_gateway_with_id_event):
        product_id = common.get_product_id(api_gateway_with_id_event)
        assert product_id == "12345678-notf-0010-1234-abcdefghijkl", "Product ID returned from API event was not as expected."

    def test_product_id_not_present(self, api_gateway_event_with_no_product_id):
        with pytest.raises(Exception) as e:
            common.get_product_id(api_gateway_event_with_no_product_id)
        assert str(e.value) == "API Event did not contain a Product ID in the path parameters.", "Exception not as expected."
