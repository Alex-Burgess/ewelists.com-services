import pytest
import boto3
from moto import mock_dynamodb2
from lists import common_table_ops
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def dynamodb_mock():
    mock = mock_dynamodb2()
    mock.start()
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = dynamodb.create_table(
        TableName='lists-unittest',
        KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}, {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{'AttributeName': 'PK', 'AttributeType': 'S'}, {'AttributeName': 'SK', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    items = fixtures.load_test_data()

    for item in items:
        table.put_item(TableName='lists-unittest', Item=item)

    yield
    mock.stop()


class TestGetList:
    def test_get_list(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        item = common_table_ops.get_list('lists-unittest', user_id, list_id)
        assert item['PK']['S'] == 'LIST#12345678-list-0001-1234-abcdefghijkl', "List returned was not as expected."

    def test_get_list_with_missing_list_exception(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0009-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            common_table_ops.get_list('lists-unittest', user_id, list_id)
        assert str(e.value) == "No list exists with this ID.", "Exception not as expected."


class TestGetUsersName:
    def test_get_users_name(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        name = common_table_ops.get_users_name('lists-unittest', user_id)
        assert name == "Test User1", "User's name was not as expected."

    def test_with_invalid_userid(self, dynamodb_mock):
        user_id = '12345678-user-0010-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            common_table_ops.get_users_name('lists-unittest', user_id)
        assert str(e.value) == "No user exists with this ID.", "Exception not as expected."


class TestGetReservedDetailsItem:
    def test_get_reserved_details(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        reserved_item = common_table_ops.get_reserved_details_item('lists-unittest', list_id, product_id, user_id)

        expected_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 1, 'name': 'Test User2', 'userId': '12345678-user-0002-1234-abcdefghijkl', 'message': 'Happy Birthday'}

        assert reserved_item == expected_item, "Reserved item was not correct."

    def test_with_no_reserved_item(self, dynamodb_mock):
        product_id = '12345678-prod-0010-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            common_table_ops.get_reserved_details_item('lists-unittest', list_id, product_id, user_id)
        assert str(e.value) == "No reserved item exists with this ID.", "Exception not as expected."


class TestGetProductItem:
    def test_get_product_item(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_item = common_table_ops.get_product_item('lists-unittest', list_id, product_id)

        expected_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 2, 'type': 'products'}

        assert product_item == expected_item, "Product item was not correct."

    def test_with_no_reserved_item(self, dynamodb_mock):
        product_id = '12345678-prod-0010-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            common_table_ops.get_product_item('lists-unittest', list_id, product_id)
        assert str(e.value) == "No product item exists with this ID.", "Exception not as expected."
