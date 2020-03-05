import pytest
import boto3
from moto import mock_dynamodb2
from lists import common_table_ops, logger
from tests import fixtures

log = logger.setup_logger()


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


class TestGetUsersDetails:
    def test_get_users_details(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        user = common_table_ops.get_users_details('lists-unittest', user_id)
        assert user['name'] == "Test User1", "User's name was not as expected."
        assert user['email'] == "test.user1@gmail.com", "User's email was not as expected."

    def test_with_invalid_userid(self, dynamodb_mock):
        user_id = '12345678-user-0010-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            common_table_ops.get_users_details('lists-unittest', user_id)
        assert str(e.value) == "No user exists with this ID.", "Exception not as expected."


class TestDoesUserHaveAccount:
    def test_user_does_not_have_account(self, dynamodb_mock):
        email = 'test.user99@gmail.com'
        assert not common_table_ops.does_user_have_account('lists-unittest', 'email-index', email)

    def test_user_does_have_account(self, dynamodb_mock):
        email = 'test.user1@gmail.com'
        id = common_table_ops.does_user_have_account('lists-unittest', 'email-index', email)
        assert id == "12345678-user-0001-1234-abcdefghijkl"


class TestGetReservedDetailsItem:
    def test_get_reserved_details(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        reserved_item = common_table_ops.get_reserved_details_item('lists-unittest', list_id, product_id, user_id)

        expected_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 1, 'name': 'Test User2', 'userId': '12345678-user-0002-1234-abcdefghijkl', 'state': 'reserved', 'reservationId': '12345678-resv-0001-1234-abcdefghijkl'}

        assert reserved_item == expected_item, "Reserved item was not correct."

    def test_with_no_reserved_item(self, dynamodb_mock):
        product_id = '12345678-prod-0010-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            common_table_ops.get_reserved_details_item('lists-unittest', list_id, product_id, user_id)
        assert str(e.value) == "Product is not reserved by user.", "Exception not as expected."


class TestGetProductItem:
    def test_get_product_item(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_item = common_table_ops.get_product_item('lists-unittest', list_id, product_id)

        expected_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 2, 'purchased': 0, 'type': 'products'}

        assert product_item == expected_item, "Product item was not correct."

    def test_with_no_reserved_item(self, dynamodb_mock):
        product_id = '12345678-prod-0010-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            common_table_ops.get_product_item('lists-unittest', list_id, product_id)
        assert str(e.value) == "No product item exists with this ID.", "Exception not as expected."


class TestCheckProductNotReservedByUser:
    def test_check_product_not_reserved_by_user(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        result = common_table_ops.check_product_not_reserved_by_user('lists-unittest', list_id, product_id, user_id)

        assert result, "Product not reserved by user."

    def test_product_already_reserved_by_user(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            common_table_ops.check_product_not_reserved_by_user('lists-unittest', list_id, product_id, user_id)
        assert str(e.value) == "Product already reserved by user.", "Exception not as expected."


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
class TestUnreserveProduct:
    def test_unreserve(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        resv_id = '12345678-resv-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        new_product_reserved_quantity = 1

        assert common_table_ops.unreserve_product('lists-unittest', list_id, product_id, resv_id, user_id, new_product_reserved_quantity)

    def test_unreserve_with_email(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0003-1234-abcdefghijkl'
        resv_id = '12345678-resv-0001-1234-abcdefghijkl'
        user_id = 'test.user99@gmail.com'
        new_product_reserved_quantity = 0

        assert common_table_ops.unreserve_product('lists-unittest', list_id, product_id, resv_id, user_id, new_product_reserved_quantity)
