import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import unreserve
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0002-1234-abcdefghijkl"

    return event


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
    # teardown: stop moto server
    mock.stop()


class TestGetReservedDetailsItem:
    def test_get_reserved_details(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        reserved_item = unreserve.get_reserved_details_item('lists-unittest', list_id, product_id)

        expected_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 1, 'name': 'Test User2', 'userId': '12345678-user-0002-1234-abcdefghijkl', 'message': 'Happy Birthday'}

        assert reserved_item == expected_item, "Reserved item was not correct."

    def test_with_no_reserved_item(self, dynamodb_mock):
        product_id = '12345678-prod-0010-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            unreserve.get_reserved_details_item('lists-unittest', list_id, product_id)
        assert str(e.value) == "No reserved item exists with this ID.", "Exception not as expected."


class TestGetProductItem:
    def test_get_product_item(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_item = unreserve.get_product_item('lists-unittest', list_id, product_id)

        expected_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'type': 'products'}

        assert product_item == expected_item, "Product item was not correct."

    def test_with_no_reserved_item(self, dynamodb_mock):
        product_id = '12345678-prod-0010-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            unreserve.get_product_item('lists-unittest', list_id, product_id)
        assert str(e.value) == "No product item exists with this ID.", "Exception not as expected."


class TestConfirmUserReservedProduct:
    def test_confirm_user_reserved_product(self):
        reserved_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 1, 'name': 'Test User2', 'userId': '12345678-user-0002-1234-abcdefghijkl', 'message': 'Happy Birthday'}
        user_id = '12345678-user-0002-1234-abcdefghijkl'
        assert unreserve.confirm_user_reserved_product(user_id, reserved_item)

    def test_bad_requestor_throws_exception(self):
        reserved_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 1, 'name': 'Test User2', 'userId': '12345678-user-0002-1234-abcdefghijkl', 'message': 'Happy Birthday'}
        user_id = '12345678-user-0003-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            unreserve.confirm_user_reserved_product(user_id, reserved_item)
        assert str(e.value) == "Requestor ID 12345678-user-0003-1234-abcdefghijkl did not match user id of reserved item user ID 12345678-user-0002-1234-abcdefghijkl."


class TestCalculateNewReservedQuantity:
    def test_subtract_1(self):
        expected_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'type': 'products'}
        new_quantity = unreserve.calculate_new_reserved_quantity(expected_item, -1)
        assert new_quantity == 0

    def test_over_subtract(self):
        expected_item = {'productId': '12345678-prod-0001-1234-abcdefghijkl', 'quantity': 3, 'reserved': 1, 'type': 'products'}
        with pytest.raises(Exception) as e:
            unreserve.calculate_new_reserved_quantity(expected_item, -2)
        assert str(e.value) == "Reserved quantity for product (1) could not be updated by -2.", "Exception message not correct."


class TestUpdateTable:
    @pytest.mark.skip(reason="transact_write_items is not implemented for moto")
    def test_update_items(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        assert unreserve.update_items('lists-unittest', list_id, product_id, 2)


class TestUnreserveMain:
    @pytest.mark.skip(reason="transact_write_items is not implemented for moto")
    def test_unreserve_product_for_user(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unreserve.unreserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['unreserved'], "Unreserve main response did not contain the correct status."

    def test_unreserve_product_not_reserved(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters'] = {"productid": "12345678-prod-0011-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
        response = unreserve.unreserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No reserved item exists with this ID.", "Error was not as expected"

    def test_unreserve_product_not_added_to_list(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0011-1234-abcdefghijkl"}
        response = unreserve.unreserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No reserved item exists with this ID.", "Error was not as expected"

    def test_unreserve_product_not_reserved_by_requestor(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0001-1234-abcdefghijkl"
        response = unreserve.unreserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "Requestor ID 12345678-user-0001-1234-abcdefghijkl did not match user id of reserved item user ID 12345678-user-0002-1234-abcdefghijkl.", "Error was not as expected"

    def test_unreserve_product_with_wrong_quantities(self, monkeypatch, dynamodb_mock, api_gateway_event):
        # Update table to break concurrency of product reserved quantity, with that of the reserved items.
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')
        key = {
            'PK': {'S': "LIST#{}".format(api_gateway_event['pathParameters']['id'])},
            'SK': {'S': "PRODUCT#{}".format(api_gateway_event['pathParameters']['productid'])}
        }

        response = dynamodb.update_item(
            TableName='lists-unittest',
            Key=key,
            UpdateExpression="set reserved = :r",
            ExpressionAttributeValues={
                ':r': {'N': str(0)},
            }
        )

        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = unreserve.unreserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "Reserved quantity for product (0) could not be updated by -1.", "Error was not as expected"
