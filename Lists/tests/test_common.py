import pytest
import os
from lists import common
from tests import fixtures

import sys
import copy
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture()
def api_gateway_with_id_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "null"

    return event


@pytest.fixture()
def api_gateway_event_with_no_list_id():
    event = fixtures.api_gateway_base_event()
    event['httpMethod'] = "POST"
    return event


@pytest.fixture()
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


@pytest.fixture()
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


@pytest.fixture()
def response_items():
    items = fixtures.load_test_response()
    return items


@pytest.fixture()
def list_query_response():
    response = [
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'SHARE#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'SHARE#12345678-user-0002-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0002-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "quantity": {"N": "2"}, "reserved": {"N": "1"}, "type": {"S": "products"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0002-1234-abcdefghijkl"}, "quantity": {"N": "3"}, "reserved": {"N": "1"}, "type": {"S": "products"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-notf-0001-1234-abcdefghijkl"}, "quantity": {"N": "2"}, "reserved": {"N": "0"}, "type": {"S": "notfound"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVED#PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "name": {"S": "Test User2"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "message": {"S": "Happy Birthday"}, "reservedAt": {"N": "1573739584"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVED#PRODUCT#12345678-prod-0002-1234-abcdefghijkl"}, "name": {"S": "Test User2"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "message": {"S": "Happy Birthday"}, "reservedAt": {"N": "1573739584"}},
    ]

    return response


def test_create_response():
    response = common.create_response(200, 'Success message')

    expected_response = {'statusCode': 200,
                         'body': 'Success message',
                         'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                         }}
    assert response == expected_response, "Create_response did not return the expected response value."


class TestGetListIdFromPath:
    def test_get_list_id(self, api_gateway_with_id_event):
        list_id = common.get_list_id(api_gateway_with_id_event)
        assert list_id == "12345678-list-0001-1234-abcdefghijkl", "List ID returned from API event was not as expected."

    def test_get_list_id_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common.get_list_id(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain a List ID in the path parameters.", "Exception not as expected."

    def test_get_list_id_empty(self, api_gateway_with_id_event):
        api_gateway_with_id_event['pathParameters']['id'] = ''
        with pytest.raises(Exception) as e:
            common.get_list_id(api_gateway_with_id_event)
        assert str(e.value) == "API Event did not contain a List ID in the path parameters.", "Exception not as expected."


class TestGetProductIdFromPath:
    def test_get_product_id(self, api_gateway_add_product_event):
        product_id = common.get_product_id(api_gateway_add_product_event)
        assert product_id == "12345678-prod-0001-1234-abcdefghijkl", "Product ID returned from API event was not as expected."

    def test_get_product_id_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common.get_product_id(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain a Product ID in the path parameters.", "Exception not as expected."

    def test_get_product_id_empty(self, api_gateway_add_product_event):
        api_gateway_add_product_event['pathParameters']['productid'] = ''
        with pytest.raises(Exception) as e:
            common.get_product_id(api_gateway_add_product_event)
        assert str(e.value) == "API Event did not contain a Product ID in the path parameters.", "Exception not as expected."


class TestGetQuantity:
    def test_get_quantity(self, api_gateway_add_product_event):
        quantity = common.get_quantity(api_gateway_add_product_event)
        assert quantity == 1, "Quantity returned from API event was not as expected."

    def test_get_quantity_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common.get_quantity(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain the quantity in the body.", "Exception not as expected."


class TestGetProductType:
    def test_get_product_type(self, api_gateway_add_product_event):
        product = common.get_product_type(api_gateway_add_product_event)
        assert product == 'products', "Product type returned from API event was not as expected."

    def test_get_product_type_of_notfound(self, api_gateway_add_product_event):
        notfound_body = copy.deepcopy(api_gateway_add_product_event)
        notfound_body['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"notfound\"\n}'
        product = common.get_product_type(notfound_body)
        assert product == 'notfound', "Product type returned from API event was not as expected."

    def test_get_wrong_product_type(self, api_gateway_add_product_event):
        wrong_body = copy.deepcopy(api_gateway_add_product_event)
        wrong_body['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"wrong\"\n}'
        with pytest.raises(Exception) as e:
            common.get_product_type(wrong_body)
        assert str(e.value) == "API Event did not contain a product type of products or notfound.", "Exception not as expected."

    def test_get_product_type_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common.get_product_type(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain the product type in the body.", "Exception not as expected."


class TestGetPostmanIdentity:
    def test_get_postman_identity(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_IDENTITY_ID', 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl')
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')

        identity = common.get_postman_identity(os.environ)
        assert identity['POSTMAN_IDENTITY_ID'] == 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl', "POSTMAN_IDENTITY_ID not as expected."
        assert identity['POSTMAN_USERPOOL_SUB'] == '12345678-user-api1-1234-abcdefghijkl', "POSTMAN_USERPOOL_SUB not as expected."

    def test_get_postman_identity_when_both_osvars_missing(self):
        with pytest.raises(Exception) as e:
            common.get_postman_identity(os.environ)
        assert str(e.value) == "POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."

    def test_get_postman_identity_when_userpool_missing(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_IDENTITY_ID', 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl')
        with pytest.raises(Exception) as e:
            common.get_postman_identity(os.environ)
        assert str(e.value) == "POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."

    def test_get_postman_identity_when_identity_id_missing(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')
        with pytest.raises(Exception) as e:
            common.get_postman_identity(os.environ)
        assert str(e.value) == "POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."


class TestGetIdentity:
    def test_get_identity(self, api_gateway_with_id_event):
        identity = common.get_identity(api_gateway_with_id_event, os.environ)
        assert identity["cognitoIdentityId"] == "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "cognitoIdentityId not as expected."
        assert identity["userPoolSub"] == "12345678-user-0001-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_postman_request(self, monkeypatch, api_gateway_postman_event):
        monkeypatch.setitem(os.environ, 'POSTMAN_IDENTITY_ID', 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl')
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')
        identity = common.get_identity(api_gateway_postman_event, os.environ)
        assert identity["cognitoIdentityId"] == "eu-west-1:12345678-user-fed1-1234-abcdefghijkl", "cognitoIdentityId not as expected."
        assert identity["userPoolSub"] == "12345678-user-api1-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_noid(self, api_gateway_event_with_no_identity):
        with pytest.raises(Exception) as e:
            common.get_identity(api_gateway_event_with_no_identity, os.environ)
        assert str(e.value) == "There was no identity context in API event.", "Exception not as expected."

    def test_get_identity_when_postman_request_and_with_no_osvars(self, api_gateway_postman_event):
        with pytest.raises(Exception) as e:
            common.get_identity(api_gateway_postman_event, os.environ)
        assert str(e.value) == "POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."


class TestGetTableName:
    def test_get_table_name(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-test')
        table_name = common.get_table_name(os.environ)
        assert table_name == "lists-test", "Table name from os environment variables was not as expected."

    def test_get_table_name_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_table_name(os.environ)
        assert str(e.value) == "TABLE_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetTableIndex:
    def test_get_table_index(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'index-test')
        index_name = common.get_table_index(os.environ)
        assert index_name == "index-test", "Index name from os environment variables was not as expected."

    def test_get_table_index_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_table_index(os.environ)
        assert str(e.value) == "INDEX_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetUserpoolId:
    def test_get_userpool_id(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'USERPOOL_ID', 'ewelists-test')
        userpool_id = common.get_userpool_id(os.environ)
        assert userpool_id == "ewelists-test", "Table name from os environment variables was not as expected."

    def test_get_userpool_name_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_userpool_id(os.environ)
        assert str(e.value) == "USERPOOL_ID environment variable not set correctly.", "Exception not as expected."


class TestConfirmOwner:
    def test_confirm_owner(self, list_query_response):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        result = common.confirm_owner(user_id, list_id, list_query_response)
        assert result, "List should be owned by user."

    def test_confirm_not_owner(self, list_query_response):
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            common.confirm_owner(user_id, list_id, list_query_response)
        assert str(e.value) == "Owner of List ID 12345678-list-0001-1234-abcdefghijkl did not match user id of requestor: 12345678-user-0002-1234-abcdefghijkl.", "Exception not thrown for list not being owned by user."


class TestConfirmListSharedWithUser:
    def test_confirm_list_shared_with_self(self, list_query_response):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        result = common.confirm_list_shared_with_user(user_id, list_id, list_query_response)
        assert result, "List should be shared with user."

    def test_confirm_list_shared_with_user(self, list_query_response):
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        result = common.confirm_list_shared_with_user(user_id, list_id, list_query_response)
        assert result, "List should be shared with user."

    def test_confirm_list_not_shared_with_user(self, list_query_response):
        user_id = '12345678-user-0010-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            common.confirm_list_shared_with_user(user_id, list_id, list_query_response)
        assert str(e.value) == "List ID 12345678-list-0001-1234-abcdefghijkl did not have a shared item with user 12345678-user-0010-1234-abcdefghijkl.", "Exception not thrown for list not being shared with user."


class TestGenerateListObject:
    def test_generate_list_object(self, list_query_response):
        items = common.generate_list_object(list_query_response)
        assert items['list']['listId'] == "12345678-list-0001-1234-abcdefghijkl", "ListId was incorrect."
        assert items['list']['title'] == "Child User1 1st Birthday", "List title was incorrect."
        assert items['list']['description'] == "A gift list for Child User1 birthday.", "List description was incorrect."
        assert items['list']['occasion'] == "Birthday", "List occasion was incorrect."

        assert len(items['products']) == 3, "Number of products was not 2."
        assert items['products']["12345678-prod-0001-1234-abcdefghijkl"] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "quantity": 2, "reserved": 1, "type": "products"}, "Product object not correct."
        assert items['products']["12345678-prod-0002-1234-abcdefghijkl"] == {"productId": "12345678-prod-0002-1234-abcdefghijkl", "quantity": 3, "reserved": 1, "type": "products"}, "Product object not correct."
        assert items['products']["12345678-notf-0001-1234-abcdefghijkl"] == {"productId": "12345678-notf-0001-1234-abcdefghijkl", "quantity": 2, "reserved": 0, "type": "notfound"}, "Product object not correct."

        assert len(items['reserved']) == 2, "Number of products reserved was not 2."
        assert items['reserved'][0] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday"}, "Reserved object not correct."
        assert items['reserved'][1] == {"productId": "12345678-prod-0002-1234-abcdefghijkl", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "message": "Happy Birthday"}, "Reserved object not correct."
