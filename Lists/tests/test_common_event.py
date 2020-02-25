import pytest
import os
import copy
from lists import common_event
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
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "null"

    return event


@pytest.fixture
def api_gateway_event_with_no_list_id():
    event = fixtures.api_gateway_base_event()
    event['httpMethod'] = "POST"
    return event


@pytest.fixture
def api_gateway_postman_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
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
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "null"
    event['requestContext']['identity'] = {}

    return event


@pytest.fixture
def api_gateway_add_product_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/product/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"quantity\": 1,\n    \"productType\": \"products\"\n}"

    return event


@pytest.fixture
def api_gateway_reserve_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/product/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/reserved/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"quantity\": 1,\n    \"message\": \"Happy birthday\"\n}"

    return event


@pytest.fixture
def api_gateway_reserve_with_email_event():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}/email/{email}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/test.user99%40gmail.com"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99%40gmail.com"}
    event['body'] = "{\n    \"quantity\": 2,\n    \"name\": \"Test User99\"\n}"

    return event


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
def api_gateway_unshare_shared_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/share/{user}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/share/12345678-user-0002-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"user": "12345678-user-0002-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"share_type\": \"SHARED\"\n}"

    return event


@pytest.fixture
def api_gateway_unshare_pending_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/share/{user}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/share/test.user4%40gmail.com"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"user": "test.user4%40gmail.com", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"share_type\": \"PENDING\"\n}"

    return event


class TestGetShareType:
    def test_get_share_type_shared(self, api_gateway_unshare_shared_event):
        type = common_event.get_share_type(api_gateway_unshare_shared_event)
        assert type == 'SHARED', "Shared type returned from API event was not as expected."

    def test_get_share_type_pending(self, api_gateway_unshare_pending_event):
        type = common_event.get_share_type(api_gateway_unshare_pending_event)
        assert type == 'PENDING', "Shared type returned from API event was not as expected."

    def test_get_wrong_share_type(self, api_gateway_unshare_pending_event):
        api_gateway_unshare_pending_event['body'] = "{\n    \"share_type\": \"WRONG\"\n}"
        with pytest.raises(Exception) as e:
            common_event.get_share_type(api_gateway_unshare_pending_event)
        assert str(e.value) == "API Event did not contain a share type of SHARED or PENDING.", "Exception not as expected."

    def test_get_share_type_with_no_body(self, api_gateway_unshare_pending_event):
        api_gateway_unshare_pending_event['body'] = None
        with pytest.raises(Exception) as e:
            common_event.get_share_type(api_gateway_unshare_pending_event)
        assert str(e.value) == "API Event did not contain a share type in the body.", "Exception not as expected."


class TestGetListIdFromPath:
    def test_get_list_id(self, api_gateway_with_id_event):
        list_id = common_event.get_list_id(api_gateway_with_id_event)
        assert list_id == "12345678-list-0001-1234-abcdefghijkl", "List ID returned from API event was not as expected."

    def test_get_list_id_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common_event.get_list_id(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain a List ID in the path parameters.", "Exception not as expected."

    def test_get_list_id_empty(self, api_gateway_with_id_event):
        api_gateway_with_id_event['pathParameters']['id'] = ''
        with pytest.raises(Exception) as e:
            common_event.get_list_id(api_gateway_with_id_event)
        assert str(e.value) == "API Event did not contain a List ID in the path parameters.", "Exception not as expected."


class TestGetProductIdFromPath:
    def test_get_product_id(self, api_gateway_add_product_event):
        product_id = common_event.get_product_id(api_gateway_add_product_event)
        assert product_id == "12345678-prod-0001-1234-abcdefghijkl", "Product ID returned from API event was not as expected."

    def test_get_product_id_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common_event.get_product_id(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain a Product ID in the path parameters.", "Exception not as expected."

    def test_get_product_id_empty(self, api_gateway_add_product_event):
        api_gateway_add_product_event['pathParameters']['productid'] = ''
        with pytest.raises(Exception) as e:
            common_event.get_product_id(api_gateway_add_product_event)
        assert str(e.value) == "API Event did not contain a Product ID in the path parameters.", "Exception not as expected."


class TestGetQuantity:
    def test_get_quantity(self, api_gateway_add_product_event):
        quantity = common_event.get_quantity(api_gateway_add_product_event)
        assert quantity == 1, "Quantity returned from API event was not as expected."

    def test_get_quantity_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common_event.get_quantity(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain the quantity in the body.", "Exception not as expected."


class TestGetMessage:
    def test_get_message(self, api_gateway_reserve_event):
        message = common_event.get_message(api_gateway_reserve_event)
        assert message == "Happy birthday", "Message returned from API event was not as expected."

    def test_get_message_when_not_present(self, api_gateway_reserve_event):
        api_gateway_reserve_event['body'] = "{\n    \"quantity\": 1\n }"
        message = common_event.get_message(api_gateway_reserve_event)
        assert message is None, "Message returned from API event was not as expected."


class TestGetProductType:
    def test_get_product_type(self, api_gateway_add_product_event):
        product = common_event.get_product_type(api_gateway_add_product_event)
        assert product == 'products', "Product type returned from API event was not as expected."

    def test_get_product_type_of_notfound(self, api_gateway_add_product_event):
        notfound_body = copy.deepcopy(api_gateway_add_product_event)
        notfound_body['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"notfound\"\n}'
        product = common_event.get_product_type(notfound_body)
        assert product == 'notfound', "Product type returned from API event was not as expected."

    def test_get_wrong_product_type(self, api_gateway_add_product_event):
        wrong_body = copy.deepcopy(api_gateway_add_product_event)
        wrong_body['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"wrong\"\n}'
        with pytest.raises(Exception) as e:
            common_event.get_product_type(wrong_body)
        assert str(e.value) == "API Event did not contain a product type of products or notfound.", "Exception not as expected."

    def test_get_product_type_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common_event.get_product_type(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain the product type in the body.", "Exception not as expected."


class TestGetIdentity:
    def test_get_identity(self, api_gateway_with_id_event):
        identity = common_event.get_identity(api_gateway_with_id_event, os.environ)
        assert identity == "12345678-user-0001-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_postman_request(self, monkeypatch, api_gateway_postman_event):
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')
        identity = common_event.get_identity(api_gateway_postman_event, os.environ)
        assert identity == "12345678-user-api1-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_postman2_request(self, monkeypatch, api_gateway_postman_event):
        api_gateway_postman_event['requestContext']['identity']['userArn'] = "arn:aws:iam::123456789012:user/ApiTestUser2"
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB2', '12345678-user-api2-1234-abcdefghijkl')
        identity = common_event.get_identity(api_gateway_postman_event, os.environ)
        assert identity == "12345678-user-api2-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_noid(self, api_gateway_event_with_no_identity):
        with pytest.raises(Exception) as e:
            common_event.get_identity(api_gateway_event_with_no_identity, os.environ)
        assert str(e.value) == "There was no identity context in API event.", "Exception not as expected."

    def test_get_identity_when_postman_request_and_with_no_osvars(self, api_gateway_postman_event):
        with pytest.raises(Exception) as e:
            common_event.get_identity(api_gateway_postman_event, os.environ)
        assert str(e.value) == "POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."


class TestGetPathParameter:
    def test_get_email(self, api_gateway_reserve_with_email_event):
        email = common_event.get_path_parameter(api_gateway_reserve_with_email_event, 'email')
        assert email == 'test.user99@gmail.com', "Path parameter returned from API event was not as expected."

    def test_get_product_id(self, api_gateway_reserve_with_email_event):
        id = common_event.get_path_parameter(api_gateway_reserve_with_email_event, 'productid')
        assert id == '12345678-prod-0001-1234-abcdefghijkl', "Path parameter returned from API event was not as expected."

    def test_get_parameter_not_present(self, api_gateway_reserve_with_email_event):
        with pytest.raises(Exception) as e:
            common_event.get_path_parameter(api_gateway_reserve_with_email_event, 'helloworld')
        assert str(e.value) == "Path did not contain a helloworld parameter.", "Exception not as expected."

    def test_get_parameter_when_null(self, api_gateway_reserve_with_email_event):
        api_gateway_reserve_with_email_event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/null"
        api_gateway_reserve_with_email_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "null"}
        with pytest.raises(Exception) as e:
            common_event.get_path_parameter(api_gateway_reserve_with_email_event, 'email')
        assert str(e.value) == "Path contained a null email parameter.", "Exception not as expected."


class TestGetBodyAttribute:
    def test_get_quantity(self, api_gateway_reserve_with_email_event):
        quantity = common_event.get_body_attribute(api_gateway_reserve_with_email_event, 'quantity')
        assert quantity == 2, "Body attribute returned from API event was not as expected."

    def test_get_name(self, api_gateway_reserve_with_email_event):
        name = common_event.get_body_attribute(api_gateway_reserve_with_email_event, 'name')
        assert name == 'Test User99', "Body attribute returned from API event was not as expected."

    def test_get_body_attribute_not_present(self, api_gateway_reserve_with_email_event):
        with pytest.raises(Exception) as e:
            common_event.get_body_attribute(api_gateway_reserve_with_email_event, 'helloworld')
        assert str(e.value) == "API Event did not contain a helloworld body attribute.", "Exception not as expected."

    def test_get_user_when_body_empty(self, api_gateway_reserve_with_email_event):
        api_gateway_reserve_with_email_event['body'] = None
        with pytest.raises(Exception) as e:
            common_event.get_body_attribute(api_gateway_reserve_with_email_event, 'name')
        assert str(e.value) == "Body was missing required attributes.", "Exception message not correct."
