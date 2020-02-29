from lists.common_entities import User, List, Product, Reserved
from lists import logger

log = logger.setup_logger()


class TestUser:
    def test_get_basic_details(self):
        user_item = {'PK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'email': {'S': 'test.user1@gmail.com'}, 'name': {'S': 'Test User1'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}}

        user = User(user_item).get_basic_details()
        assert user['name'] == 'Test User1', "User name was not Test User."
        assert user['email'] == 'test.user1@gmail.com', "User email was not test.user@gmail.com."
        assert user['userId'] == '12345678-user-0001-1234-abcdefghijkl', "User ID was not correct."

    def test_get_basic_details_with_no_name(self):
        user_item = {'PK': {'S': 'USER#12345678-user-0002-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0002-1234-abcdefghijkl'}, 'email': {'S': 'test.user2@gmail.com'}, 'userId': {'S': '12345678-user-0002-1234-abcdefghijkl'}}

        user = User(user_item).get_basic_details()
        assert user['name'] == 'test.user2@gmail.com', "User name was not test.user2@gmail.com."
        assert user['email'] == 'test.user2@gmail.com', "User email was not test.user2@gmail.com."
        assert user['userId'] == '12345678-user-0002-1234-abcdefghijkl', "User ID was not correct."


class TestList:
    def test_get_details(self):
        list_item = {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}}

        list = List(list_item).get_details()
        assert list['listId'] == '12345678-list-0001-1234-abcdefghijkl', "List ID was not 12345678-list-0001-1234-abcdefghijkl."
        assert list['title'] == "Child User1 1st Birthday", "List Title was not as expected."
        assert list['description'] == "A gift list for Child User1 birthday.", "List description was not as expected."
        assert list['eventDate'] == '31 October 2018', "List event date was not 01 September 2019."
        assert list['occasion'] == 'Birthday', "List occasion was not Birthday."
        assert list['imageUrl'] == '/images/celebration-default.jpg', "List imageUrl was not as expected."
        assert list['listOwner'] == '12345678-user-0001-1234-abcdefghijkl', "List occasion was not correct."

    def test_get_details_with_no_date(self):
        list_item = {"PK": {'S': "LIST#12345678-list-0002-1234-abcdefghijkl"}, "SK": {'S': "USER#12345678-user-0001-1234-abcdefghijkl"}, "userId": {'S': "12345678-user-0001-1234-abcdefghijkl"}, "title": {'S': "Child User1 Christmas List"}, "occasion": {'S': "Christmas"}, "listId": {'S': "12345678-list-0002-1234-abcdefghijkl"}, "listOwner": {'S': "12345678-user-0001-1234-abcdefghijkl"}, "createdAt": {'S': "2018-11-01T10:00:00"}, "description": {'S': "A gift list for Child User1 Christmas."}, "imageUrl": {'S': "/images/christmas-default.jpg"}}
        list = List(list_item).get_details()

        assert list['listId'] == '12345678-list-0002-1234-abcdefghijkl', "List ID was not 12345678-list-0002-1234-abcdefghijkl."
        assert list['title'] == "Child User1 Christmas List", "List Title was not as expected."
        assert list['description'] == "A gift list for Child User1 Christmas.", "List description was not as expected."
        assert list['occasion'] == 'Christmas', "List occasion was not correct."
        assert list['listOwner'] == '12345678-user-0001-1234-abcdefghijkl', "List occasion was not correct."


class TestProduct:
    def test_get_details(self):
        product_item = {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "quantity": {"N": "2"}, "reserved": {"N": "1"}, "type": {"S": "products"}}
        product = Product(product_item).get_details()

        assert product['productId'] == '12345678-prod-0001-1234-abcdefghijkl', "Product ID was not correct."
        assert product['quantity'] == 2, "Product quanity was not correct."
        assert product['reserved'] == 1, "Product reserved quantity was not correct."
        assert product['type'] == 'products', "Product reserved type was not correct."


class TestReserved:
    def test_get_details(self):
        reserved_item = {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVED#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl"}, "name": {"S": "Test User2"}, "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "message": {"S": "Happy Birthday"}, "reservedAt": {"N": "1573739584"}}
        reserved = Reserved(reserved_item).get_details()

        assert reserved['productId'] == '12345678-prod-0001-1234-abcdefghijkl', "Product ID was not correct."
        assert reserved['quantity'] == 1, "Reserved quanity was not 1."
        assert reserved['name'] == "Test User2", "Reserved name was not correct."
        assert reserved['message'] == 'Happy Birthday', "Reserved message was not correct."
        assert reserved['userId'] == '12345678-user-0002-1234-abcdefghijkl', "Reserved userId was not correct."

    def test_get_item_if_no_message(self):
        reserved_item = {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVED#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl"}, "name": {"S": "Test User2"}, "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "reservedAt": {"N": "1573739584"}}
        reserved = Reserved(reserved_item).get_details()

        assert reserved['productId'] == '12345678-prod-0001-1234-abcdefghijkl', "Product ID was not correct."
        assert reserved['quantity'] == 1, "Reserved quanity was not 1."
        assert reserved['name'] == "Test User2", "Reserved name was not correct."
        assert not reserved.get('message'), "Reserved message was not correct."
        assert reserved['userId'] == '12345678-user-0002-1234-abcdefghijkl', "Reserved userId was not correct."
