import pytest
import os
import json
import mock
from lists import reserve, logger

log = logger.setup_test_logger()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'INDEX_NAME', 'email-index')
    monkeypatch.setitem(os.environ, 'TEMPLATE_NAME', 'Email-Template')
    monkeypatch.setitem(os.environ, 'DOMAIN_NAME', 'https://test.ewelists.com')

    return monkeypatch


@pytest.mark.skip(reason="transact_write_items is not implemented for moto")
class TestCreateReservation:
    def test_create_reservation(self, dynamodb_mock):
        new_product_reserved_quantity = 1
        product_key = {
            'PK': {'S': "LIST#12345678-list-0001-1234-abcdefghijkl"},
            'SK': {'S': "PRODUCT#12345678-prod-0002-1234-abcdefghijkl"}
        }

        reservation_item = {
            'PK': {'S': "LIST#12345678-list-0001-1234-abcdefghijkl"},
            'SK': {'S': "RESERVATION#12345678-prod-0002-1234-abcdefghijkl#12345678-user-0001-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"},
            'reservationId': {'S': '12345678-resv-0001-1234-abcdefghijkl'},
            'productId': {'S': '12345678-prod-0001-1234-abcdefghijkl'},
            'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'},
            'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'},
            'name': {'S': 'Test User'},
            'email': {'S': 'test.user1@gmail.com'},
            'quantity': {'N': '1'},
            'state': {'S': 'reserved'},
            'reservedAt': {'N': '1111111111111'},
            'listTitle': {'S': 'Test List Title'},
            'productType': {'S': 'products'}
        }

        assert reserve.create_reservation('lists-unittest', new_product_reserved_quantity, product_key, reservation_item)


class TestCreateEmailData:
    def test_create_email_data(self):
        domain_name = 'http://localhost:3000'
        name = 'Test User'
        resv_id = '12345678-resv-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        list_title = 'Test List Title'
        quantity = 2
        product = {
            "type": "products",
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "productUrl": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "imageUrl": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }

        data = reserve.create_email_data(domain_name, name, resv_id, list_id, list_title, quantity, product)

        expected_data = {
            "name": "Test User",
            "list_title": "Test List Title",
            "list_url": "http://localhost:3000/lists/12345678-list-0001-1234-abcdefghijkl",
            "quantity": 2,
            "confirm_url": "http://localhost:3000/reserve/12345678-resv-0001-1234-abcdefghijkl",
            "edit_url": "http://localhost:3000/reserve/12345678-resv-0001-1234-abcdefghijkl",
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "product_url": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "image_url": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }

        assert len(data) == 10, "Number of fields in email data was not as expected."
        assert data == expected_data, "Email data json object was not as expected."

    def test_create_email_data_with_amazon_product(self):
        domain_name = 'http://localhost:3000'
        name = 'Test User'
        resv_id = '12345678-resv-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        list_title = 'Test List Title'
        quantity = 1
        product = {
            "type": "products",
            "brand": "Baby Bjorn",
            "details": "Travel Cot",
            "productUrl": "https://www.amazon.co.uk/BABYBJ%C3%96RN-Travel-Easy-Anthracite-transport/dp/B07DJ5KX53/ref=as_li_ss_il?ref_=ast_sto_dp&amp;th=1&amp;psc=1&amp;linkCode=li3&amp;tag=ewelists-21&amp;linkId=53810d50be55070942f429bbbb607867",
            "imageUrl": "//ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8&amp;ASIN=B07DJ5KX53&amp;Format=_SL250_&amp;ID=AsinImage&amp;MarketPlace=GB&amp;ServiceVersion=20070822&amp;WS=1&amp;tag=ewelists-21"
        }

        data = reserve.create_email_data(domain_name, name, resv_id, list_id, list_title, quantity, product)

        expected_image_url = 'https://ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8&amp;ASIN=B07DJ5KX53&amp;Format=_SL250_&amp;ID=AsinImage&amp;MarketPlace=GB&amp;ServiceVersion=20070822&amp;WS=1&amp;tag=ewelists-21'
        assert len(data) == 10, "Number of fields in email data was not as expected."
        assert data['image_url'] == expected_image_url, "Email data json object was not as expected."


class TestCreateReservationItem:
    def test_create_reservation_item(self):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        list_title = 'Test List Title'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        product_type = 'products'
        user = {
            'id': '12345678-user-0001-1234-abcdefghijkl',
            'name': 'Test User1',
            'email': 'test.user1@gmail.com'
        }
        request_reserve_quantity = 1
        resv_id = '12345678-resv-0001-1234-abcdefghijkl'

        object = reserve.create_reservation_item(list_id, list_title, product_id, product_type, resv_id, user, request_reserve_quantity)

        assert list(object.keys()) == ['PK', 'SK', 'reservationId', 'productId', 'userId', 'listId', 'name', 'email', 'quantity', 'state', 'reservedAt', 'listTitle', 'productType']

        assert object['PK']['S'] == "LIST#12345678-list-0001-1234-abcdefghijkl", "Object was not as expected."
        assert object['SK']['S'] == "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0001-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl", "Object was not as expected."
        assert object['reservationId']['S'] == "12345678-resv-0001-1234-abcdefghijkl", "Object was not as expected."
        assert object['productId']['S'] == "12345678-prod-0001-1234-abcdefghijkl", "Object was not as expected."
        assert object['userId']['S'] == "12345678-user-0001-1234-abcdefghijkl", "Object was not as expected."
        assert object['listId']['S'] == "12345678-list-0001-1234-abcdefghijkl", "Object was not as expected."
        assert object['name']['S'] == "Test User1", "Object was not as expected."
        assert object['email']['S'] == "test.user1@gmail.com", "Object was not as expected."
        assert object['quantity']['N'] == "1", "Object was not as expected."
        assert object['state']['S'] == "reserved", "Object was not as expected."
        assert len(object['reservedAt']['N']) == 10, "Object was not as expected."
        assert object['listTitle']['S'] == "Test List Title", "Object was not as expected."
        assert object['productType']['S'] == "products", "Object was not as expected."


class TestReserveMain:
    def test_no_list_id_path_parameter(self, env_vars, api_reserve_event):
        api_reserve_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "null", "email": "test.user99@gmail.com"}
        response = reserve.reserve_main(api_reserve_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null id parameter.', "Error for missing environment variable was not as expected."

    def test_no_product_id_path_parameter(self, env_vars, api_reserve_event):
        api_reserve_event['pathParameters'] = {"productid": "null", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        response = reserve.reserve_main(api_reserve_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null productid parameter.', "Error for missing environment variable was not as expected."

    def test_no_email_path_parameter(self, env_vars, api_reserve_event):
        api_reserve_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "null"}
        response = reserve.reserve_main(api_reserve_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null email parameter.', "Error for missing environment variable was not as expected."

    def test_reserve_no_name_for_non_user(self, env_vars, api_reserve_event, dynamodb_mock):
        api_reserve_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        api_reserve_event['body'] = json.dumps({
            "quantity": 1,
            "title": "Child User1 1st Birthday",
            "product": {
                "type": "products",
                "brand": "Mamas and Papas",
                "details": "Balloon Print Zip All-in-One",
                "productUrl": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
                "imageUrl": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
            }
        })

        response = reserve.reserve_main(api_reserve_event)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event did not contain a name body attribute.', "Reserve error was not as expected."

    def test_reserve_with_no_body(self, env_vars, api_reserve_event, dynamodb_mock):
        api_reserve_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        api_reserve_event['body'] = None

        response = reserve.reserve_main(api_reserve_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Body was missing required attributes.', "Reserve error was not as expected."

    # TODO - If transact_write_items is implemented for moto (https://github.com/spulec/moto/issues/2424), we can rely solely on dynamodb_mock.
    # We could also query table to test objects are created correctly. This is covered by integration testing though.
    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[]))
    @mock.patch("lists.reserve.create_reservation", mock.MagicMock(return_value=True))
    @mock.patch("lists.common.send_email", mock.MagicMock(return_value=True))
    def test_reserve_product_not_yet_reserved(self, env_vars, api_reserve_event, dynamodb_mock):
        api_reserve_event['pathParameters'] = {"productid": "12345678-prod-0002-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user2@gmail.com"}
        response = reserve.reserve_main(api_reserve_event)
        body = json.loads(response['body'])
        assert len(body['reservation_id']) == 36, "Reservation ID was not returned."

    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[]))
    @mock.patch("lists.reserve.create_reservation", mock.MagicMock(return_value=True))
    @mock.patch("lists.common.send_email", mock.MagicMock(return_value=True))
    def test_reserve_product_with_some_reserved(self, env_vars, api_reserve_event, dynamodb_mock):
        response = reserve.reserve_main(api_reserve_event)
        body = json.loads(response['body'])
        assert len(body['reservation_id']) == 36, "Reservation ID was not returned."

    def test_over_reserve_product(self, env_vars, api_reserve_event, dynamodb_mock):
        api_reserve_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user1@gmail.com"}
        api_reserve_event['body'] = json.dumps({
            "quantity": 4,
            "title": "Child User1 1st Birthday",
            "product": {
                "type": "products",
                "brand": "Mamas and Papas",
                "details": "Balloon Print Zip All-in-One",
                "productUrl": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
                "imageUrl": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
            }
        })

        response = reserve.reserve_main(api_reserve_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Reserved quantity for product (2) could not be updated by 4 as exceeds required quantity (3).', "Reserve error was not as expected."

    def test_reserve_product_not_added_to_list(self, env_vars, api_reserve_event, dynamodb_mock):
        api_reserve_event['pathParameters'] = {"productid": "12345678-prod-1000-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user1@gmail.com"}

        response = reserve.reserve_main(api_reserve_event)
        body = json.loads(response['body'])
        assert body['error'] == 'No product item exists with this ID.', "Reserve error was not as expected."

    @mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[
        {
            "quantity": {"N": "1"},
            "reservedAt": {"N": "1584982686"},
            "userId": {"S": "12345678-user-0003-1234-abcdefghijkl"},
            "reservationId": {"S": "12345678-resv-0002-1234-abcdefghijkl"},
            "SK": {"S": "RESERVED#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0003-1234-abcdefghijkl#12345678-resv-0002-1234-abcdefghijkl"},
            "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
            "name": {"S": "Test User2"},
            "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"},
            "state": {"S": "reserved"}
        }
    ]))
    def test_reserve_product_already_reserved_by_user(self, env_vars, api_reserve_event, dynamodb_mock):
        response = reserve.reserve_main(api_reserve_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Product already reserved by user.', "Reserve error was not as expected."


@mock.patch("lists.common_table_ops.get_reservation_items_query", mock.MagicMock(return_value=[]))
@mock.patch("lists.reserve.create_reservation", mock.MagicMock(return_value=True))
@mock.patch("lists.common.send_email", mock.MagicMock(return_value=True))
def test_handler(api_reserve_event, env_vars, dynamodb_mock):
    response = reserve.handler(api_reserve_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert len(body['reservation_id']) == 36, "Reservation ID was not returned."
