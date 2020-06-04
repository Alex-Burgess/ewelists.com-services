import boto3
import pytest
import mock
from lists import common_table_ops, logger

log = logger.setup_test_logger()


class TestGetListQuery:
    def test_get_list_query(self, dynamodb_mock):
        list_id = "12345678-list-0001-1234-abcdefghijkl"
        items = common_table_ops.get_list_query('lists-unittest', list_id)
        assert len(items) == 14, "Number of items deleted was not as expected."

    def test_get_list_query_no_table_name(self, dynamodb_mock):
        list_id = "12345678-list-0001-1234-abcdefghijkl"

        with pytest.raises(Exception) as e:
            common_table_ops.get_list_query('lists-unittes', list_id)
        assert str(e.value) == "Unexpected error when getting list item from table.", "Exception not as expected."

    def test_get_list_query_for_item_that_does_not_exist(self, dynamodb_mock):
        list_id = "12345678-list-0009-1234-abcdefghijkl"

        with pytest.raises(Exception) as e:
            common_table_ops.get_list_query('lists-unittest', list_id)
        assert str(e.value) == "List 12345678-list-0009-1234-abcdefghijkl does not exist.", "Exception not as expected."


class TestGetList:
    def test_get_list(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        item = common_table_ops.get_list('lists-unittest', user_id, list_id)
        assert item['listId'] == '12345678-list-0001-1234-abcdefghijkl', "List returned was not as expected."

    def test_get_list_with_missing_list_exception(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0009-1234-abcdefghijkl'
        item = common_table_ops.get_list('lists-unittest', user_id, list_id)
        assert item == {}, "Exception not as expected."


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


class TestGetUserIdFromEmail:
    def test_user_does_not_have_account(self, dynamodb_mock):
        email = 'test.user99@gmail.com'
        assert not common_table_ops.get_user_id_from_email('lists-unittest', 'email-index', email)

    def test_user_does_have_account(self, dynamodb_mock):
        email = 'test.user1@gmail.com'
        id = common_table_ops.get_user_id_from_email('lists-unittest', 'email-index', email)
        assert id == "12345678-user-0001-1234-abcdefghijkl"


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


@pytest.mark.skip(reason="Query with begins_with is not implemented for moto")
class TestGetReservationItems:
    def test_get_reservation_items(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'

        expected_item = [
            {
                "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
                "SK": {"S": "RESERVED#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"},
                "reservationId": {"S": "12345678-resv-0001-1234-abcdefghijkl"},
                "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"},
                "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"},
                "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"},
                "name": {"S": "Test User2"},
                "email": {"S": "test.user2@gmail.com"},
                "quantity": {"N": "1"},
                "state": {"S": "reserved"},
                "reservedAt": {"N": "1584982686"},
                "listTitle": {"S": "Birthday List"},
                "productType": {"S": "products"}
            }
        ]

        result = common_table_ops.get_reservation_items_query('lists-unittest', list_id, product_id, user_id)
        assert result == expected_item


class TestGetReservations:
    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[
        {
            "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
            "SK": {"S": "RESERVED#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"},
            "reservationId": {"S": "12345678-resv-0001-1234-abcdefghijkl"},
            "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"},
            "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"},
            "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"},
            "listOwnerId": {"S": "12345678-user-0001-1234-abcdefghijkl"},
            "name": {"S": "Test User2"},
            "email": {"S": "test.user2@gmail.com"},
            "quantity": {"N": "1"},
            "state": {"S": "reserved"},
            "reservedAt": {"N": "1584982686"},
            "listTitle": {"S": "Birthday List"},
            "productType": {"S": "products"}
        }
    ]))
    def test_get_reservation(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'

        reserved_item = common_table_ops.get_reservations('lists-unittest', list_id, product_id, user_id)

        expected_items = [{
            'reservationId': '12345678-resv-0001-1234-abcdefghijkl',
            'productId': '12345678-prod-0001-1234-abcdefghijkl',
            'userId': '12345678-user-0002-1234-abcdefghijkl',
            'listId': '12345678-list-0001-1234-abcdefghijkl',
            "listOwnerId": "12345678-user-0001-1234-abcdefghijkl",
            'name': 'Test User2',
            'email': 'test.user2@gmail.com',
            'quantity': 1,
            'state': 'reserved',
            'listTitle': 'Birthday List',
            'productType': 'products',
            }]

        assert reserved_item == expected_items, "Reserved item was not correct."

    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[
        {
            "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
            "SK": {"S": "RESERVED#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"},
            "reservationId": {"S": "12345678-resv-0001-1234-abcdefghijkl"},
            "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"},
            "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"},
            "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"},
            "listOwnerId": {"S": "12345678-user-0001-1234-abcdefghijkl"},
            "name": {"S": "Test User2"},
            "email": {"S": "test.user2@gmail.com"},
            "quantity": {"N": "1"},
            "state": {"S": "reserved"},
            "reservedAt": {"N": "1584982686"},
            "listTitle": {"S": "Birthday List"},
            "productType": {"S": "products"}
        },
        {
            "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
            "SK": {"S": "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0006-1234-abcdefghijkl"},
            "reservationId": {"S": "12345678-resv-0006-1234-abcdefghijkl"},
            "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"},
            "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"},
            "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"},
            "listOwnerId": {"S": "12345678-user-0001-1234-abcdefghijkl"},
            "name": {"S": "Test User2"},
            "email": {"S": "test.user2@gmail.com"},
            "quantity": {"N": "1"},
            "state": {"S": "purchased"},
            "reservedAt": {"N": "1584982686"},
            "listTitle": {"S": "Birthday List"},
            "productType": {"S": "products"}
        }
    ]))
    def test_get_reservations(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'

        reserved_item = common_table_ops.get_reservations('lists-unittest', list_id, product_id, user_id)

        assert len(reserved_item) == 2, "Number of reserved items was not as expected."

    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[]))
    def test_with_no_reserved_item(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        product_id = '12345678-prod-0010-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            common_table_ops.get_reservations('lists-unittest', list_id, product_id, user_id)
        assert str(e.value) == "Product is not reserved by user.", "Exception not as expected."


class TestCheckProductNotReservedByUser:
    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[]))
    def test_product_not_reserved_by_user(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0012-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'

        result = common_table_ops.check_product_not_reserved_by_user('lists-unittest', list_id, product_id, user_id)
        assert result, "Not reserved should be true."

    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[
        {
            "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
            "SK": {"S": "RESERVED#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"},
            "reservationId": {"S": "12345678-resv-0001-1234-abcdefghijkl"},
            "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"},
            "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"},
            "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"},
            "name": {"S": "Test User2"},
            "email": {"S": "test.user2@gmail.com"},
            "quantity": {"N": "1"},
            "state": {"S": "reserved"},
            "reservedAt": {"N": "1584982686"},
            "listTitle": {"S": "Birthday List"},
            "productType": {"S": "products"}
        }
    ]))
    def test_product_already_reserved_by_user(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            common_table_ops.check_product_not_reserved_by_user('lists-unittest', list_id, product_id, user_id)
        assert str(e.value) == "Product already reserved by user.", "Exception not as expected."

    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[
        {
            "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
            "SK": {"S": "RESERVATION#12345678-prod-0004-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0006-1234-abcdefghijkl"},
            "reservationId": {"S": "12345678-resv-0006-1234-abcdefghijkl"},
            "productId": {"S": "12345678-prod-0004-1234-abcdefghijkl"},
            "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"},
            "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"},
            "name": {"S": "Test User2"},
            "email": {"S": "test.user2@gmail.com"},
            "quantity": {"N": "1"},
            "state": {"S": "purchased"},
            "reservedAt": {"N": "1584982686"},
            "listTitle": {"S": "Birthday List"},
            "productType": {"S": "products"}
        }
    ]))
    def test_confirmed_purchased(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        product_id = '12345678-prod-0004-1234-abcdefghijkl'

        result = common_table_ops.check_product_not_reserved_by_user('lists-unittest', list_id, product_id, user_id)
        assert result, "Not reserved should be true."

    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[
        {
            "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
            "SK": {"S": "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"},
            "reservationId": {"S": "12345678-resv-0001-1234-abcdefghijkl"},
            "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"},
            "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"},
            "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"},
            "name": {"S": "Test User2"},
            "email": {"S": "test.user2@gmail.com"},
            "quantity": {"N": "1"},
            "state": {"S": "reserved"},
            "reservedAt": {"N": "1584982686"},
            "listTitle": {"S": "Birthday List"},
            "productType": {"S": "products"}
        },
        {
            "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
            "SK": {"S": "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0006-1234-abcdefghijkl"},
            "reservationId": {"S": "12345678-resv-0006-1234-abcdefghijkl"},
            "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"},
            "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"},
            "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"},
            "name": {"S": "Test User2"},
            "email": {"S": "test.user2@gmail.com"},
            "quantity": {"N": "1"},
            "state": {"S": "purchased"},
            "reservedAt": {"N": "1584982686"},
            "listTitle": {"S": "Birthday List"},
            "productType": {"S": "products"}
        }
    ]))
    def test_purchased_and_reserved(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            common_table_ops.check_product_not_reserved_by_user('lists-unittest', list_id, product_id, user_id)
        assert str(e.value) == "Product already reserved by user.", "Exception not as expected."

    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[
        {
            "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
            "SK": {"S": "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"},
            "reservationId": {"S": "12345678-resv-0001-1234-abcdefghijkl"},
            "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"},
            "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"},
            "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"},
            "name": {"S": "Test User2"},
            "email": {"S": "test.user2@gmail.com"},
            "quantity": {"N": "1"},
            "state": {"S": "purchased"},
            "reservedAt": {"N": "1584982686"},
            "listTitle": {"S": "Birthday List"},
            "productType": {"S": "products"}
        },
        {
            "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
            "SK": {"S": "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0006-1234-abcdefghijkl"},
            "reservationId": {"S": "12345678-resv-0006-1234-abcdefghijkl"},
            "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"},
            "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"},
            "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"},
            "name": {"S": "Test User2"},
            "email": {"S": "test.user2@gmail.com"},
            "quantity": {"N": "1"},
            "state": {"S": "purchased"},
            "reservedAt": {"N": "1584982686"},
            "listTitle": {"S": "Birthday List"},
            "productType": {"S": "products"}
        }
    ]))
    def test_purchased_twice(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'

        result = common_table_ops.check_product_not_reserved_by_user('lists-unittest', list_id, product_id, user_id)
        assert result, "Not reserved should be true."


class TestGetReservation:
    def test_get_reservation(self, dynamodb_mock):
        reservation = common_table_ops.get_reservation('lists-unittest', 'reservationId-index', '12345678-resv-0001-1234-abcdefghijkl')
        assert reservation['reservationId'] == "12345678-resv-0001-1234-abcdefghijkl"
        assert reservation['listId'] == "12345678-list-0001-1234-abcdefghijkl"

    def test_missing_reservation(self, dynamodb_mock):
        with pytest.raises(Exception) as e:
            common_table_ops.get_reservation('lists-unittest', 'reservationId-index', '12345678-resv-1111-1234-abcdefghijkl')
        assert str(e.value) == "Reservation ID does not exist.", "Exception not as expected."

    def test_duplicate_reservation_ids(self, dynamodb_mock):
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        dynamodb.put_item(
            TableName='lists-unittest',
            Item={
                'PK': {'S': "LIST#12345678-list-any1-1234-abcdefghijkl"},
                'SK': {'S': "RESERVATION#12345678-prod-any1-1234-abcdefghijkl#12345678-user-0001-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"},
                'reservationId': {'S': '12345678-resv-0001-1234-abcdefghijkl'},
                'productId': {'S': '12345678-prod-any1-1234-abcdefghijkl'},
                'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'},
                'listId': {'S': '12345678-list-any1-1234-abcdefghijkl'},
                'name': {'S': 'Test User'},
                'email': {'S': 'test.user@gmail.com'},
                'quantity': {'N': '1'},
                'state': {'S': 'reserved'},
                'reservedAt': {'N': '1111111'},
                'listTitle': {'S': 'List Title'},
                'productType': {'S': 'products'}
            },
        )

        with pytest.raises(Exception) as e:
            common_table_ops.get_reservation('lists-unittest', 'reservationId-index', '12345678-resv-0001-1234-abcdefghijkl')
        assert str(e.value) == "Multiple items were found with same reservation id.", "Exception not as expected."
