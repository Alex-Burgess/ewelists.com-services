import pytest
import os
from lists import common, logger
from moto import mock_ses
import boto3

log = logger.setup_test_logger()


@pytest.fixture
def reservation_item():
    return {
        'PK': "LIST#12345678-list-any1-1234-abcdefghijkl",
        'SK': "RESERVATION#12345678-prod-any1-1234-abcdefghijkl#12345678-user-0001-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl",
        'reservationId': '12345678-resv-0001-1234-abcdefghijkl',
        'productId': '12345678-prod-any1-1234-abcdefghijkl',
        'userId': '12345678-user-0001-1234-abcdefghijkl',
        'listId': '12345678-list-any1-1234-abcdefghijkl',
        'name': 'Test User',
        'email': 'test.user@gmail.com',
        'quantity': '1',
        'state': 'reserved',
        'reservedAt': '1111111',
        'listTitle': 'List Title',
        'productType': 'products'
    }


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
    def test_get_email(self, api_base_event):
        api_base_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        email = common.get_path_parameter(api_base_event, 'email')
        assert email == 'test.user99@gmail.com', "Path parameter returned from API event was not as expected."

    def test_get_product_id(self, api_base_event):
        api_base_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        id = common.get_path_parameter(api_base_event, 'productid')
        assert id == '12345678-prod-0001-1234-abcdefghijkl', "Path parameter returned from API event was not as expected."

    def test_get_parameter_not_present(self, api_base_event):
        api_base_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        with pytest.raises(Exception) as e:
            common.get_path_parameter(api_base_event, 'helloworld')
        assert str(e.value) == "Path did not contain a helloworld parameter.", "Exception not as expected."

    def test_get_parameter_when_null(self, api_base_event):
        api_base_event['pathParameters'] = {"email": "null"}
        with pytest.raises(Exception) as e:
            common.get_path_parameter(api_base_event, 'email')
        assert str(e.value) == "Path contained a null email parameter.", "Exception not as expected."


class TestGetBodyAttribute:
    def test_get_name(self, api_base_event):
        api_base_event['body'] = "{\n    \"name\": \"Test User99\"\n}"
        name = common.get_body_attribute(api_base_event, 'name')
        assert name == 'Test User99', "Body attribute returned from API event was not as expected."

    def test_get_body_attribute_not_present(self, api_base_event):
        api_base_event['body'] = "{\n    \"name\": \"Test User99\"\n}"
        with pytest.raises(Exception) as e:
            common.get_body_attribute(api_base_event, 'helloworld')
        assert str(e.value) == "API Event did not contain a helloworld body attribute.", "Exception not as expected."

    def test_get_user_when_body_empty(self, api_base_event):
        api_base_event['body'] = None
        with pytest.raises(Exception) as e:
            common.get_body_attribute(api_base_event, 'name')
        assert str(e.value) == "Body was missing required attributes.", "Exception message not correct."


class TestGetBodyAttributeIfExists:
    def test_get_notes(self, api_base_event):
        api_base_event['body'] = "{\n    \"notes\": \"I would size medium\"\n}"
        notes = common.get_body_attribute_if_exists(api_base_event, 'notes')
        assert notes == 'I would size medium', "Body attribute returned from API event was not as expected."

    def test_notes_attribute_not_present(self, api_base_event):
        api_base_event['body'] = "{\n    \"name\": \"Test User99\"\n}"
        notes = common.get_body_attribute_if_exists(api_base_event, 'notes')
        assert notes is None, "Body attribute returned from API event was not as expected."

    def test_get_notes_when_body_empty(self, api_base_event):
        api_base_event['body'] = None
        with pytest.raises(Exception) as e:
            common.get_body_attribute_if_exists(api_base_event, 'notes')
        assert str(e.value) == "Body was missing required attributes.", "Exception message not correct."


class TestParseEmail:
    def test_parse_email(self):
        assert common.parse_email(' Test.user@gmail.com ') == 'test.user@gmail.com'
        assert common.parse_email(' Test.user@googlemail.com ') == 'test.user@googlemail.com'


class TestIsGoogleEmail:
    def test_with_gmail(self):
        assert common.is_google_email('test.user@gmail.com')

    def test_with_googlemail(self):
        assert common.is_google_email('test.user@googlemail.com')

    def test_with_not_google_email(self):
        assert not common.is_google_email('test.user@random.com')


class TestConfirmOwner:
    def test_confirm_owner(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        result = common.confirm_owner('lists-unittest', user_id, list_id)
        assert result, "List should be owned by user."

    def test_confirm_not_owner(self, dynamodb_mock):
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            common.confirm_owner('lists-unittest', user_id, list_id)
        assert str(e.value) == "User 12345678-user-0002-1234-abcdefghijkl was not owner of List 12345678-list-0001-1234-abcdefghijkl.", "Exception not thrown for list not being owned by user."

    def test_list_does_not_exist(self, dynamodb_mock):
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        list_id = '12345678-list-9999-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            common.confirm_owner('lists-unittest', user_id, list_id)
        assert str(e.value) == "List 12345678-list-9999-1234-abcdefghijkl does not exist.", "Exception not thrown for list not being owned by user."


class TestConfirmReservationOwner:
    def test_confirm_reservation_owner(self, reservation_item):
        assert common.confirm_reservation_owner(reservation_item, '12345678-user-0001-1234-abcdefghijkl')

    def test_confirm_reservation_owner_with_email(self, reservation_item):
        assert common.confirm_reservation_owner(reservation_item, 'test.user@gmail.com')

    def test_not_reservation_owner(self, reservation_item):
        with pytest.raises(Exception) as e:
            common.confirm_reservation_owner(reservation_item, '12345678-user-0002-1234-abcdefghijkl')
        assert str(e.value) == "Requestor is not reservation owner.", "Exception not as expected."

    def test_not_reservation_owner_with_email(self, reservation_item):
        with pytest.raises(Exception) as e:
            common.confirm_reservation_owner(reservation_item, 'test.user2@gmail.confirmed')
        assert str(e.value) == "Requestor is not reservation owner.", "Exception not as expected."


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


@mock_ses
class TestSendEmail:
    def test_send_email(self):
        ses = boto3.client('ses', region_name='eu-west-1')
        ses.verify_email_identity(EmailAddress="contact@ewelists.com")

        ses.create_template(
            Template={
                'TemplateName': 'reserve-template',
                'SubjectPart': 'string',
                'TextPart': 'string',
                'HtmlPart': 'string'
            }
        )

        assert common.send_email('eweuser8@gmail.com', 'Ewe User8', 'reserve-template')


class TestGetUser:
    def test_get_user_with_no_account(self, dynamodb_mock, api_no_auth_base_event):
        api_no_auth_base_event['pathParameters'] = {"email": "test.user99@gmail.com"}
        api_no_auth_base_event['body'] = "{\n    \"name\": \"Test User99\"\n}"
        user = common.get_user(api_no_auth_base_event, os.environ, 'lists-unittest', 'email-index')

        assert user['id'] == 'test.user99@gmail.com'
        assert user['email'] == 'test.user99@gmail.com'
        assert user['name'] == 'Test User99'
        assert not user['exists']

    def test_get_user_with_account(self, dynamodb_mock, api_no_auth_base_event):
        api_no_auth_base_event['pathParameters'] = {"email": "test.user1@gmail.com"}
        api_no_auth_base_event['body'] = "{\n    \"name\": \"Test User1\"\n}"
        user = common.get_user(api_no_auth_base_event, os.environ, 'lists-unittest', 'email-index')
        assert user['id'] == '12345678-user-0001-1234-abcdefghijkl'
        assert user['email'] == 'test.user1@gmail.com'
        assert user['name'] == 'Test User1'
        assert user['exists']

    def test_get_user_when_body_empty(self, dynamodb_mock, api_no_auth_base_event):
        api_no_auth_base_event['pathParameters'] = {"email": "test.user99@gmail.com"}
        api_no_auth_base_event['body'] = None
        user = common.get_user(api_no_auth_base_event, os.environ, 'lists-unittest', 'email-index')
        assert user['id'] == 'test.user99@gmail.com'
        assert user['email'] == 'test.user99@gmail.com'
        assert 'name' not in user
        assert not user['exists']

    def test_get_user_when_email_null(self, dynamodb_mock, api_no_auth_base_event):
        api_no_auth_base_event['pathParameters'] = {"email": "null"}
        with pytest.raises(Exception) as e:
            common.get_user(api_no_auth_base_event, os.environ, 'lists-unittest', 'email-index')
        assert str(e.value) == "Path contained a null email parameter.", "Exception message not correct."

    def test_get_user_when_name_not_in_body(self, dynamodb_mock, api_no_auth_base_event):
        api_no_auth_base_event['pathParameters'] = {"email": "test.user99@gmail.com"}
        api_no_auth_base_event['body'] = "{\n    \"wrongname\": \"Test User99\"\n}"
        with pytest.raises(Exception) as e:
            common.get_user(api_no_auth_base_event, os.environ, 'lists-unittest', 'email-index')
        assert str(e.value) == "API Event did not contain a name body attribute.", "Exception message not correct."


class TestGetProductType:
    def test_get_product_type(self, api_base_event):
        api_base_event['body'] = "{\n    \"quantity\": 1,\n    \"productType\": \"products\"\n}"
        product = common.get_product_type(api_base_event)
        assert product == 'products', "Product type returned from API event was not as expected."

    def test_get_product_type_of_notfound(self, api_base_event):
        api_base_event['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"notfound\"\n}'
        product = common.get_product_type(api_base_event)
        assert product == 'notfound', "Product type returned from API event was not as expected."

    def test_get_wrong_product_type(self, api_base_event):
        api_base_event['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"wrong\"\n}'
        with pytest.raises(Exception) as e:
            common.get_product_type(api_base_event)
        assert str(e.value) == "API Event did not contain a product type of products or notfound.", "Exception not as expected."

    def test_get_product_type_when_not_present(self, api_base_event):
        with pytest.raises(Exception) as e:
            common.get_product_type(api_base_event)
        assert str(e.value) == "API Event did not contain the product type in the body.", "Exception not as expected."


class TestGetIdentity:
    def test_get_identity(self, api_base_event):
        identity = common.get_identity(api_base_event, os.environ)
        assert identity == "12345678-user-0001-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_postman_request(self, monkeypatch, api_postman_event):
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')
        identity = common.get_identity(api_postman_event, os.environ)
        assert identity == "12345678-user-api1-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_postman2_request(self, monkeypatch, api_postman_event):
        api_postman_event['requestContext']['identity']['userArn'] = "arn:aws:iam::123456789012:user/ApiTestUser2"
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB2', '12345678-user-api2-1234-abcdefghijkl')
        identity = common.get_identity(api_postman_event, os.environ)
        assert identity == "12345678-user-api2-1234-abcdefghijkl", "userPoolSub not as expected."

    @pytest.mark.usefixtures("api_no_auth_base_event")
    def test_get_identity_when_noid(self, api_no_auth_base_event):
        with pytest.raises(Exception) as e:
            common.get_identity(api_no_auth_base_event, os.environ)
        assert str(e.value) == "There was no identity in the API event.", "Exception not as expected."

    def test_get_identity_when_postman_request_and_with_no_osvars(self, api_postman_event):
        with pytest.raises(Exception) as e:
            common.get_identity(api_postman_event, os.environ)
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

    def test_gift_is_purchased_raises_exception(self):
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
        assert str(e.value) == "Product was not reserved. State = purchased.", "Exception message not correct."

    def test_gift_is_cancelled_raises_exception(self):
        reserved_item = {
            'reservationId': '12345678-resv-0001-1234-abcdefghijkl',
            'name': 'Test User2',
            'productId': '12345678-prod-0001-1234-abcdefghijkl',
            'userId': '12345678-user-0002-1234-abcdefghijkl',
            'quantity': 1,
            'state': 'cancelled'
        }

        with pytest.raises(Exception) as e:
            common.gift_is_reserved(reserved_item)
        assert str(e.value) == "Product was not reserved. State = cancelled.", "Exception message not correct."


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


class TestCreateReservationKey:
    def test_create_product_key(self):
        item = {
            'reservationId': '12345678-resv-0001-1234-abcdefghijkl',
            'productId': '12345678-prod-0001-1234-abcdefghijkl',
            'userId': '12345678-user-0002-1234-abcdefghijkl',
            'listId': '12345678-list-0001-1234-abcdefghijkl',
            'name': 'Test User2',
            'email': 'test.user2@gmail.com',
            'quantity': 1,
            'state': 'reserved',
            'listTitle': 'Birthday List',
            'productType': 'products',
        }

        expected_object = {
            'PK': {'S': "LIST#12345678-list-0001-1234-abcdefghijkl"},
            'SK': {'S': "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"}
        }

        key = common.create_reservation_key(item)
        assert key == expected_object, "Key was not as expected."


class TestCheckImageUrl:
    def test_url_with_https_prefix(self):
        url = 'https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$'
        result = common.check_image_url(url)
        assert result == 'https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$'

    def test_url_without_https_prefix(self):
        url = '//ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8&amp;ASIN=B07DJ5KX53&amp;Format=_SL250_&amp;ID=AsinImage&amp;MarketPlace=GB&amp;ServiceVersion=20070822&amp;WS=1&amp;tag=ewelists-21'
        result = common.check_image_url(url)
        assert result == 'https://ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8&amp;ASIN=B07DJ5KX53&amp;Format=_SL250_&amp;ID=AsinImage&amp;MarketPlace=GB&amp;ServiceVersion=20070822&amp;WS=1&amp;tag=ewelists-21'


class TestGetListDetails:
    def test_get_list_details(self, dynamodb_mock):
        list_id = "12345678-list-0001-1234-abcdefghijkl"
        list = common.get_list_details('lists-unittest', list_id)

        expected_list_object = {
            'description': 'A gift list for Child User1 birthday.',
            'eventDate': '31 October 2018',
            'imageUrl': '/images/celebration-default.jpg',
            'listId': '12345678-list-0001-1234-abcdefghijkl',
            'listOwner': '12345678-user-0001-1234-abcdefghijkl',
            'occasion': 'Birthday',
            'state': 'open',
            'title': 'Child User1 1st Birthday'
        }

        assert list == expected_list_object, "List details were not as expected"
