import pytest
from lists.entities import User, List, Product
import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture()
def response_items():
    response_items = [
        {'PK': {'S': 'USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'}, 'SK': {'S': 'USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'}, 'email': {'S': 'test.user@gmail.com'}, 'name': {'S': 'Test User'}, 'userId': {'S': 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'}},
        {'PK': {'S': 'LIST#12345678-abcd-abcd-123456789112'}, 'SK': {'S': 'USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'}, 'userId': {'S': 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'}, 'title': {'S': "Api Child's 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-abcd-abcd-123456789112'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'listOwner': {'S': 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'}, 'description': {'S': 'A gift list for Api Childs birthday.'}, 'eventDate': {'S': '2019-09-01'}},
        {"quantity": {"N": "1"}, "reserved": {"N": "0"}, "SK": {"S": "PRODUCT#1009"}, "PK": {"S": "LIST#76a2fe57-9fac-4a0d-9225-1942949889ba"}}
    ]

    return response_items


class TestUser:
    def test_get_basic_details(self, response_items):
        user = User(response_items[0]).get_basic_details()

        assert user['name'] == 'Test User', "User name was not Test User."
        assert user['email'] == 'test.user@gmail.com', "User email was not test.user@gmail.com."


class TestList:
    def test_get_details(self, response_items):
        list = List(response_items[1]).get_details()

        assert list['listId'] == '12345678-abcd-abcd-123456789112', "List ID was not 12345678-abcd-abcd-123456789112."
        assert list['title'] == "Api Child's 1st Birthday", "List Title was not as expected."
        assert list['description'] == "A gift list for Api Childs birthday.", "List description was not as expected."
        assert list['occasion'] == 'Birthday', "List occasion was not Birthday."


class TestProduct:
    def test_get_details(self, response_items):
        product = Product(response_items[2]).get_details()

        assert product['productId'] == '1009', "Product ID was not 1009."
        assert product['quantity'] == 1, "Product quanity was not 1."
        assert product['reserved'] == 0, "Product reserved quantity was not 0."
