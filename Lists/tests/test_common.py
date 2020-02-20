import pytest
from lists import common
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


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


def test_create_response():
    response = common.create_response(200, 'Success message')

    expected_response = {'statusCode': 200,
                         'body': 'Success message',
                         'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                         }}
    assert response == expected_response, "Create_response did not return the expected response value."


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


class TestCalculateNewReservedQuantity:
    def test_subtract_1(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'type': 'products'}
        new_quantity = common.calculate_new_reserved_quantity(product_item, -1)
        assert new_quantity == 0

    def test_no_update(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'type': 'products'}
        new_quantity = common.calculate_new_reserved_quantity(product_item, 0)
        assert new_quantity == 1

    def test_add_2(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'type': 'products'}
        new_quantity = common.calculate_new_reserved_quantity(product_item, 2)
        assert new_quantity == 3

    def test_over_subtract(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'type': 'products'}
        with pytest.raises(Exception) as e:
            common.calculate_new_reserved_quantity(product_item, -2)
        assert str(e.value) == "Reserved quantity for product (1) could not be updated by -2.", "Exception message not correct."

    def test_over_add(self):
        product_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'type': 'products'}
        with pytest.raises(Exception) as e:
            common.calculate_new_reserved_quantity(product_item, 3)
        assert str(e.value) == "Reserved quantity for product (1) could not be updated by 3 as exceeds required quantity (3).", "Exception message not correct."


@pytest.mark.skip(reason="Not sure how to mock ses.")
class TestSendEmail:
    def test_send_email(self):
        email = 'eweuser8@gmail.com'
        name = 'Ewe User8'
        template = 'reserve-template'
        assert common.send_email(email, name, template)
