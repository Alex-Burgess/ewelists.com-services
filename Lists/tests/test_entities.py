import pytest
from lists.entities import User, List, Product, Reserved
import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture()
def response_items():
    response_items = [
        {'PK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'email': {'S': 'test.user@gmail.com'}, 'name': {'S': 'Test User'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}},
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Api Child's 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'description': {'S': 'A gift list for Api Childs birthday.'}, 'eventDate': {'S': '01 September 2019'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
        {'PK': {'S': 'LIST#12345678-list-0002-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Api Child's 2nd Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0002-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'description': {'S': 'A gift list for Api Childs birthday.'}, 'eventDate': {'S': '01 September 2020'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}},
        {"quantity": {"N": "1"}, "reserved": {"N": "1"}, "type": {"S": "products"}, "SK": {"S": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "reservedDetails": {"L": [{"M": {"name": {"S": "Test User"}, "userId": {"S": "12345678-user-0005-1234-abcdefghijkl"}, "reservedNumber": {"N": "1"}, "message": {"S": "Happy Birthday"}, "reservedAt": {"N": "1573739584"}}}]}},
        {"SK": {"S": "RESERVED#PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "name": {"S": "Test User1"}, "userId": {"S": "12345678-user-0004-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "message": {"S": "Happy Birthday"}, "reservedAt": {"N": "1573739584"}}
    ]

    return response_items


class TestUser:
    def test_get_basic_details(self, response_items):
        user = User(response_items[0]).get_basic_details()

        # assert user['name'] == 'Test User', "User name was not Test User."
        assert user['email'] == 'test.user@gmail.com', "User email was not test.user@gmail.com."


class TestList:
    def test_get_details(self, response_items):
        list = List(response_items[1]).get_details()

        assert list['listId'] == '12345678-list-0001-1234-abcdefghijkl', "List ID was not 12345678-list-0001-1234-abcdefghijkl."
        assert list['title'] == "Api Child's 1st Birthday", "List Title was not as expected."
        assert list['description'] == "A gift list for Api Childs birthday.", "List description was not as expected."
        assert list['eventDate'] == '01 September 2019', "List event date was not 01 September 2019."
        assert list['occasion'] == 'Birthday', "List occasion was not Birthday."
        assert list['imageUrl'] == '/images/celebration-default.jpg', "List imageUrl was not as expected."

    def test_get_details_with_no_date(self, response_items):
        list = List(response_items[2]).get_details()

        assert list['listId'] == '12345678-list-0002-1234-abcdefghijkl', "List ID was not 12345678-list-0002-1234-abcdefghijkl."
        assert list['title'] == "Api Child's 2nd Birthday", "List Title was not as expected."
        assert list['description'] == "A gift list for Api Childs birthday.", "List description was not as expected."
        assert list['occasion'] == 'Birthday', "List occasion was not Birthday."


class TestProduct:
    def test_get_details(self, response_items):
        product = Product(response_items[3]).get_details()

        assert product['productId'] == '12345678-prod-0001-1234-abcdefghijkl', "Product ID was not correct."
        assert product['quantity'] == 1, "Product quanity was not 1."
        assert product['reserved'] == 1, "Product reserved quantity was not 0."
        assert product['type'] == 'products', "Product reserved quantity was not 0."


class TestReserved:
    def test_get_details(self, response_items):
        reserved = Reserved(response_items[4]).get_details()

        assert reserved['productId'] == '12345678-prod-0001-1234-abcdefghijkl', "Product ID was not correct."
        assert reserved['quantity'] == 1, "Product quanity was not 1."
        assert reserved['name'] == "Test User1", "Product reserved quantity was not 0."
        assert reserved['message'] == 'Happy Birthday', "Product reserved quantity was not 0."
        assert reserved['userId'] == '12345678-user-0004-1234-abcdefghijkl', "Product reserved quantity was not 0."
