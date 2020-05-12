import pytest
import os
import mock
import json
from lists import purchase, logger

log = logger.setup_test_logger()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'RESERVATIONID_INDEX', 'reservationId-index')
    monkeypatch.setitem(os.environ, 'TEMPLATE_NAME', 'Email-Template')
    monkeypatch.setitem(os.environ, 'DOMAIN_NAME', 'https://test.ewelists.com')

    return monkeypatch


class TestNewReservedQuantity:
    def test_new_reserved_quantity(self):
        assert purchase.new_reserved_quantity(1, 1) == 0, "New quantity not as expected."
        assert purchase.new_reserved_quantity(2, 1) == 1, "New quantity not as expected."


class TestNewPurchasedQuantity:
    def test_new_purchased_quantity(self):
        assert purchase.new_purchased_quantity(0, 1) == 1, "New quantity not as expected."
        assert purchase.new_purchased_quantity(2, 1) == 3, "New quantity not as expected."


class TestCreateEmailData:
    def test_create_email_data(self):
        domain_name = 'http://localhost:3000'
        name = 'Test User'
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

        data = purchase.create_email_data(domain_name, name, list_id, list_title, quantity, product)

        expected_data = {
            "name": "Test User",
            "list_title": "Test List Title",
            "list_url": "http://localhost:3000/lists/12345678-list-0001-1234-abcdefghijkl",
            "quantity": 2,
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "product_url": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "image_url": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }

        assert len(data) == 8, "Number of fields in email data was not as expected."
        assert data == expected_data, "Email data json object was not as expected."

    def test_create_email_data_with_amazon_product(self):
        domain_name = 'http://localhost:3000'
        name = 'Test User'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        list_title = 'Test List Title'
        quantity = 2
        product = {
            "type": "products",
            "brand": "Baby Bjorn",
            "details": "Travel Cot",
            "productUrl": "https://www.amazon.co.uk/BABYBJ%C3%96RN-Travel-Easy-Anthracite-transport/dp/B07DJ5KX53/ref=as_li_ss_il?ref_=ast_sto_dp&amp;th=1&amp;psc=1&amp;linkCode=li3&amp;tag=ewelists-21&amp;linkId=53810d50be55070942f429bbbb607867",
            "imageUrl": "//ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8&amp;ASIN=B07DJ5KX53&amp;Format=_SL250_&amp;ID=AsinImage&amp;MarketPlace=GB&amp;ServiceVersion=20070822&amp;WS=1&amp;tag=ewelists-21"
        }

        data = purchase.create_email_data(domain_name, name, list_id, list_title, quantity, product)

        expected_image_url = 'https://ws-eu.amazon-adsystem.com/widgets/q?_encoding=UTF8&amp;ASIN=B07DJ5KX53&amp;Format=_SL250_&amp;ID=AsinImage&amp;MarketPlace=GB&amp;ServiceVersion=20070822&amp;WS=1&amp;tag=ewelists-21'
        assert len(data) == 8, "Number of fields in email data was not as expected."
        assert data['image_url'] == expected_image_url, "Email data json object was not as expected."


class TestPurchaseMain:
    def test_no_reservation_id(self, env_vars, api_purchase_event):
        api_purchase_event['pathParameters'] = {"reservationid": "null", "email": "test.user2@gmail.com"}
        response = purchase.purchase_main(api_purchase_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null reservationid parameter.', "Error for missing environment variable was not as expected."

    def test_no_email(self, env_vars, api_purchase_event):
        api_purchase_event['pathParameters'] = {"reservationid": "12345678-resv-0002-1234-abcdefghijkl", "email": "null"}
        response = purchase.purchase_main(api_purchase_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Path contained a null email parameter.', "Error for missing environment variable was not as expected."

    @mock.patch("lists.purchase.update_product_and_reservation", mock.MagicMock(return_value=[True]))
    @mock.patch("lists.common.send_email", mock.MagicMock(return_value=[True]))
    def test_confirm_purchase(self, env_vars, api_purchase_event, dynamodb_mock):
        response = purchase.purchase_main(api_purchase_event)
        body = json.loads(response['body'])
        assert body['purchased'], "Error for missing environment variable was not as expected."

    def test_confirm_reservation_already_confirmed_by_user_with_account(self, env_vars, api_purchase_event, dynamodb_mock):
        api_purchase_event['pathParameters'] = {"reservationid": "12345678-resv-0006-1234-abcdefghijkl", "email": "test.user2@gmail.com"}
        response = purchase.purchase_main(api_purchase_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Product was not reserved. State = purchased.', "Error for missing environment variable was not as expected."

    def test_confirm_reservation_already_confirmed_by_user_with_no_account(self, env_vars, api_purchase_event, dynamodb_mock):
        api_purchase_event['pathParameters'] = {"reservationid": "12345678-resv-0007-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        response = purchase.purchase_main(api_purchase_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Product was not reserved. State = purchased.', "Error for missing environment variable was not as expected."

    def test_confirm_reservation_that_was_unreserved(self, env_vars, api_purchase_event, dynamodb_mock):
        api_purchase_event['pathParameters'] = {"reservationid": "12345678-resv-0008-1234-abcdefghijkl", "email": "test.user2@gmail.com"}
        response = purchase.purchase_main(api_purchase_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Product was not reserved. State = cancelled.', "Error for missing environment variable was not as expected."

    def test_reserve_with_no_body(self, env_vars, api_purchase_event, dynamodb_mock):
        api_purchase_event['pathParameters'] = {"reservationid": "12345678-resv-0003-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
        api_purchase_event['body'] = None

        response = purchase.purchase_main(api_purchase_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Body was missing required attributes.', "Reserve error was not as expected."


@mock.patch("lists.purchase.update_product_and_reservation", mock.MagicMock(return_value=[True]))
@mock.patch("lists.common.send_email", mock.MagicMock(return_value=[True]))
def test_handler_with_existing_user(api_purchase_event, env_vars, dynamodb_mock):
    response = purchase.handler(api_purchase_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert body['purchased'], "purchase was not confirmed."


@mock.patch("lists.purchase.update_product_and_reservation", mock.MagicMock(return_value=[True]))
@mock.patch("lists.common.send_email", mock.MagicMock(return_value=[True]))
def test_handler_with_no_account_user(api_purchase_event, env_vars, dynamodb_mock):
    api_purchase_event['pathParameters'] = {"reservationid": "12345678-resv-0003-1234-abcdefghijkl", "email": "test.user99@gmail.com"}
    response = purchase.handler(api_purchase_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert body['purchased'], "purchase was not confirmed."
