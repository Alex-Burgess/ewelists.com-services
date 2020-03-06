import pytest
import os
import boto3
from moto import mock_dynamodb2
from lists import common, logger
from tests import fixtures

log = logger.setup_logger()


@pytest.fixture()
def response_items():
    items = fixtures.load_test_response()
    return items


@pytest.fixture()
def list_query_response():
    response = [
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'SHARED#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'SHARED#12345678-user-0002-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0002-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "quantity": {"N": "2"}, "reserved": {"N": "1"}, "type": {"S": "products"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0002-1234-abcdefghijkl"}, "quantity": {"N": "3"}, "reserved": {"N": "1"}, "type": {"S": "products"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-notf-0001-1234-abcdefghijkl"}, "quantity": {"N": "2"}, "reserved": {"N": "0"}, "type": {"S": "notfound"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVED#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl"}, "name": {"S": "Test User2"}, "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "message": {"S": "Happy Birthday"}, "reservedAt": {"N": "1573739584"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVED#12345678-prod-0002-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl"}, "name": {"S": "Test User2"}, "productId": {"S": "12345678-prod-0002-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "message": {"S": "Happy Birthday"}, "reservedAt": {"N": "1573739584"}},
    ]

    return response


@pytest.fixture
def api_gateway_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"

    return event


@pytest.fixture
def api_gateway_postman_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = None

    event['requestContext']['identity'] = {
        "cognitoIdentityPoolId": None,
        "accountId": "123456789012",
        "cognitoIdentityId": None,
        "caller": "ABCDEFGPDMJL4EB35H6H",
        "sourceIp": "5.81.150.55",
        "principalOrgId": "o-d8jj6dyqv2",
        "accessKey": "ABCDEFGPDMJL4EB35H6H",
        "cognitoAuthenticationType": None,
        "cognitoAuthenticationProvider": None,
        "userArn": "arn:aws:iam::123456789012:user/ApiTestUser",
        "userAgent": "PostmanRuntime/7.15.2",
        "user": "ABCDEFGPDMJL4EB35H6H"
    }

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
def api_gateway_event_with_email():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}/email/{email}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/test.user99@gmail.com"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
    event['body'] = "{\n    \"name\": \"Test User99\"\n}"

    return event


@pytest.fixture
def api_gateway_event_with_email_and_account():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}/email/{email}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/test.user1@gmail.com"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user1@gmail.com"}
    event['body'] = "{\n    \"name\": \"Test User1\"\n}"

    return event


@pytest.fixture
def api_gateway_event_with_null_email():
    event = fixtures.api_gateway_no_auth_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}/email/{email}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/null"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "null"}
    event['body'] = "{\n    \"name\": \"Test User99\"\n}"

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


def test_create_response():
    response = common.create_response(200, 'Success message')

    expected_response = {'statusCode': 200,
                         'body': 'Success message',
                         'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                         }}
    assert response == expected_response, "Create_response did not return the expected response value."


class TestGetEnvironmentVariable:
    def test_get_variable(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-test')
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        assert table_name == "lists-test", "Table name from os environment variables was not as expected."

    def test_get_with_variable_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_env_variable(os.environ, 'TABLE_NAME')
        assert str(e.value) == "TABLE_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetPathParameter:
    def test_get_email(self, api_gateway_event_with_email):
        email = common.get_path_parameter(api_gateway_event_with_email, 'email')
        assert email == 'test.user99@gmail.com', "Path parameter returned from API event was not as expected."

    def test_get_product_id(self, api_gateway_event_with_email):
        id = common.get_path_parameter(api_gateway_event_with_email, 'productid')
        assert id == '12345678-prod-0001-1234-abcdefghijkl', "Path parameter returned from API event was not as expected."

    def test_get_parameter_not_present(self, api_gateway_event_with_email):
        with pytest.raises(Exception) as e:
            common.get_path_parameter(api_gateway_event_with_email, 'helloworld')
        assert str(e.value) == "Path did not contain a helloworld parameter.", "Exception not as expected."

    def test_get_parameter_when_null(self, api_gateway_event_with_email):
        api_gateway_event_with_email['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/null"
        api_gateway_event_with_email['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "null"}
        with pytest.raises(Exception) as e:
            common.get_path_parameter(api_gateway_event_with_email, 'email')
        assert str(e.value) == "Path contained a null email parameter.", "Exception not as expected."


class TestGetBodyAttribute:
    def test_get_name(self, api_gateway_event_with_email):
        name = common.get_body_attribute(api_gateway_event_with_email, 'name')
        assert name == 'Test User99', "Body attribute returned from API event was not as expected."

    def test_get_body_attribute_not_present(self, api_gateway_event_with_email):
        with pytest.raises(Exception) as e:
            common.get_body_attribute(api_gateway_event_with_email, 'helloworld')
        assert str(e.value) == "API Event did not contain a helloworld body attribute.", "Exception not as expected."

    def test_get_user_when_body_empty(self, api_gateway_event_with_email):
        api_gateway_event_with_email['body'] = None
        with pytest.raises(Exception) as e:
            common.get_body_attribute(api_gateway_event_with_email, 'name')
        assert str(e.value) == "Body was missing required attributes.", "Exception message not correct."


class TestParseEmail:
    def test_parse_email(self):
        assert common.parse_email(' Test.user@gmail.com ') == 'test.user@gmail.com'
        assert common.parse_email(' Test.user@googlemail.com ') == 'test.user@gmail.com'


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


class TestCalculateNewReservedQuantity:
    def test_subtract_1(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'purchased': 0, 'type': 'products'}
        new_quantity = common.calculate_new_reserved_quantity(product_item, -1)
        assert new_quantity == 0

    def test_no_update(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'purchased': 0, 'type': 'products'}
        new_quantity = common.calculate_new_reserved_quantity(product_item, 0)
        assert new_quantity == 1

    def test_add_2(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'purchased': 0, 'type': 'products'}
        new_quantity = common.calculate_new_reserved_quantity(product_item, 2)
        assert new_quantity == 3

    def test_over_subtract(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1,  'purchased': 0, 'type': 'products'}
        with pytest.raises(Exception) as e:
            common.calculate_new_reserved_quantity(product_item, -2)
        assert str(e.value) == "Reserved quantity for product (1) could not be updated by -2.", "Exception message not correct."

    def test_over_add(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'purchased': 0, 'type': 'products'}
        with pytest.raises(Exception) as e:
            common.calculate_new_reserved_quantity(product_item, 3)
        assert str(e.value) == "Reserved quantity for product (1) could not be updated by 3 as exceeds required quantity (3).", "Exception message not correct."

    def test_over_add_with_purchased(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'purchased': 1, 'type': 'products'}
        with pytest.raises(Exception) as e:
            common.calculate_new_reserved_quantity(product_item, 2)
        assert str(e.value) == "Reserved quantity for product (1) could not be updated by 2 as exceeds required quantity (3).", "Exception message not correct."


@pytest.mark.skip(reason="Not sure how to mock ses.")
class TestSendEmail:
    def test_send_email(self):
        email = 'eweuser8@gmail.com'
        name = 'Ewe User8'
        template = 'reserve-template'
        assert common.send_email(email, name, template)


class TestGetUser:
    def test_get_user_with_no_account(self, dynamodb_mock, api_gateway_event_with_email):
        user = common.get_user(api_gateway_event_with_email, os.environ, 'lists-unittest', 'email-index')
        assert user['id'] == 'test.user99@gmail.com'
        assert user['email'] == 'test.user99@gmail.com'
        assert user['name'] == 'Test User99'
        assert not user['exists']

    def test_get_user_with_account(self, dynamodb_mock, api_gateway_event_with_email_and_account):
        user = common.get_user(api_gateway_event_with_email_and_account, os.environ, 'lists-unittest', 'email-index')
        assert user['id'] == '12345678-user-0001-1234-abcdefghijkl'
        assert user['email'] == 'test.user1@gmail.com'
        assert user['name'] == 'Test User1'
        assert user['exists']

    def test_get_user_when_body_empty(self, dynamodb_mock, api_gateway_event_with_email):
        api_gateway_event_with_email['body'] = None
        user = common.get_user(api_gateway_event_with_email, os.environ, 'lists-unittest', 'email-index')
        assert user['id'] == 'test.user99@gmail.com'
        assert user['email'] == 'test.user99@gmail.com'
        assert 'name' not in user
        assert not user['exists']

    def test_get_user_when_email_null(self, dynamodb_mock, api_gateway_event_with_null_email):
        with pytest.raises(Exception) as e:
            common.get_user(api_gateway_event_with_null_email, os.environ, 'lists-unittest', 'email-index')
        assert str(e.value) == "Path contained a null email parameter.", "Exception message not correct."

    def test_get_user_when_name_not_in_body(self, dynamodb_mock, api_gateway_event_with_email):
        api_gateway_event_with_email['body'] = "{\n    \"wrongname\": \"Test User99\"\n}"
        with pytest.raises(Exception) as e:
            common.get_user(api_gateway_event_with_email, os.environ, 'lists-unittest', 'email-index')
        assert str(e.value) == "API Event did not contain a name body attribute.", "Exception message not correct."


class TestGetProductType:
    def test_get_product_type(self, api_gateway_add_product_event):
        product = common.get_product_type(api_gateway_add_product_event)
        assert product == 'products', "Product type returned from API event was not as expected."

    def test_get_product_type_of_notfound(self, api_gateway_add_product_event):
        api_gateway_add_product_event['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"notfound\"\n}'
        product = common.get_product_type(api_gateway_add_product_event)
        assert product == 'notfound', "Product type returned from API event was not as expected."

    def test_get_wrong_product_type(self, api_gateway_add_product_event):
        api_gateway_add_product_event['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"wrong\"\n}'
        with pytest.raises(Exception) as e:
            common.get_product_type(api_gateway_add_product_event)
        assert str(e.value) == "API Event did not contain a product type of products or notfound.", "Exception not as expected."

    def test_get_product_type_when_not_present(self, api_gateway_event):
        with pytest.raises(Exception) as e:
            common.get_product_type(api_gateway_event)
        assert str(e.value) == "API Event did not contain the product type in the body.", "Exception not as expected."


class TestGetIdentity:
    def test_get_identity(self, api_gateway_event):
        identity = common.get_identity(api_gateway_event, os.environ)
        assert identity == "12345678-user-0003-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_postman_request(self, monkeypatch, api_gateway_postman_event):
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')
        identity = common.get_identity(api_gateway_postman_event, os.environ)
        assert identity == "12345678-user-api1-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_postman2_request(self, monkeypatch, api_gateway_postman_event):
        api_gateway_postman_event['requestContext']['identity']['userArn'] = "arn:aws:iam::123456789012:user/ApiTestUser2"
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB2', '12345678-user-api2-1234-abcdefghijkl')
        identity = common.get_identity(api_gateway_postman_event, os.environ)
        assert identity == "12345678-user-api2-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_noid(self, api_gateway_event):
        api_gateway_event['requestContext']['identity'] = {}

        with pytest.raises(Exception) as e:
            common.get_identity(api_gateway_event, os.environ)
        assert str(e.value) == "There was no identity context in API event.", "Exception not as expected."

    def test_get_identity_when_postman_request_and_with_no_osvars(self, api_gateway_postman_event):
        with pytest.raises(Exception) as e:
            common.get_identity(api_gateway_postman_event, os.environ)
        assert str(e.value) == "POSTMAN_USERPOOL_SUB environment variable not set correctly.", "Exception not as expected."


class TestGiftIsReserved:
    def test_gift_is_reserved(self):
        reserved_item = {
            'reservationId': '12345678-resv-0001-1234-abcdefghijkl',
            'name': 'Test User2',
            'productId': '12345678-prod-0001-1234-abcdefghijkl',
            'userId': '12345678-user-0002-1234-abcdefghijkl',
            'quantity': 1,
            'state': 'reserved'
        }

        assert common.gift_is_reserved(reserved_item), "Reservation was already purchased"

    def test_gift_is_purchased_raises_exceptions(self):
        reserved_item = {
            'reservationId': '12345678-resv-0001-1234-abcdefghijkl',
            'name': 'Test User2',
            'productId': '12345678-prod-0001-1234-abcdefghijkl',
            'userId': '12345678-user-0002-1234-abcdefghijkl',
            'quantity': 1,
            'state': 'purchased'
        }

        with pytest.raises(Exception) as e:
            common.gift_is_reserved(reserved_item)
        assert str(e.value) == "Product was already purchased.", "Exception message not correct."


class TestCreateProductKey:
    def test_create_product_key(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'

        expected_object = {
            'PK': {'S': "LIST#12345678-list-0001-1234-abcdefghijkl"},
            'SK': {'S': "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}
        }

        key = common.create_product_key(list_id, product_id)
        assert key == expected_object, "Product key was not as expected."


class TestCreateReservedKey:
    def test_create_product_key(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        user = {
            'id': '12345678-user-0001-1234-abcdefghijkl',
            'name': 'Test User1',
            'email': 'test.user1x@gmail.com'
        }

        expected_object = {
            'PK': {'S': "LIST#12345678-list-0001-1234-abcdefghijkl"},
            'SK': {'S': "RESERVED#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0001-1234-abcdefghijkl"}
        }

        key = common.create_reserved_key(list_id, product_id, user)
        assert key == expected_object, "Key was not as expected."


class TestCreateReservationKey:
    def test_create_product_key(self):
        id = '12345678-resv-0001-1234-abcdefghijkl'

        expected_object = {
            'PK': {'S': "RESERVATION#12345678-resv-0001-1234-abcdefghijkl"},
            'SK': {'S': "RESERVATION#12345678-resv-0001-1234-abcdefghijkl"}
        }

        key = common.create_reservation_key(id)
        assert key == expected_object, "Key was not as expected."
