import pytest
import os
import json
import boto3
from moto import mock_dynamodb2
from lists import update_reservation, logger
from tests import fixtures

log = logger.setup_logger()


@pytest.fixture
def api_gateway_event():
    # User 2 will update its reserved quantity of product 1 from 1 to 2.
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/lists/{id}/reserve/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "PUT"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"quantity\": 2\n}"
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


class TestCalculateDifferenceToReservedItemQuantity:
    def test_increase_from_1_to_2(self):
        current_quantity = 1
        reserved_item = {"productId": "12345678-notf-0001-1234-abcdefghijkl", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": current_quantity, "message": "Happy Birthday"}
        difference = update_reservation.calculate_difference_to_reserved_item_quantity(reserved_item, 2)
        assert difference == 1

    def test_increase_from_1_to_3(self):
        current_quantity = 1
        reserved_item = {"productId": "12345678-notf-0001-1234-abcdefghijkl", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": current_quantity, "message": "Happy Birthday"}
        difference = update_reservation.calculate_difference_to_reserved_item_quantity(reserved_item, 3)
        assert difference == 2

    def test_decrease_from_3_to_1(self):
        current_quantity = 3
        reserved_item = {"productId": "12345678-notf-0001-1234-abcdefghijkl", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": current_quantity, "message": "Happy Birthday"}
        difference = update_reservation.calculate_difference_to_reserved_item_quantity(reserved_item, 1)
        assert difference == -2

    def test_decrease_to_0(self):
        current_quantity = 1
        reserved_item = {"productId": "12345678-notf-0001-1234-abcdefghijkl", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": current_quantity, "message": "Happy Birthday"}
        with pytest.raises(Exception) as e:
            update_reservation.calculate_difference_to_reserved_item_quantity(reserved_item, 0)
        assert str(e.value) == "Reserved quantity (1) for product (12345678-notf-0001-1234-abcdefghijkl) for user (12345678-user-0002-1234-abcdefghijkl) cannot be reduced to 0.", "Exception message not correct."

    def test_keep_at_1(self):
        current_quantity = 1
        reserved_item = {"productId": "12345678-notf-0001-1234-abcdefghijkl", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": current_quantity, "message": "Happy Birthday"}
        with pytest.raises(Exception) as e:
            update_reservation.calculate_difference_to_reserved_item_quantity(reserved_item, 1)
        assert str(e.value) == "There was no difference in update request to reserved item.", "Exception message not correct."


class TestUpdateReserveMain:
    @pytest.mark.skip(reason="transact_write_items is not implemented for moto")
    def test_update_reserve_main(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = update_reservation.update_reserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['updated'], "Update reserve main response did not contain the correct status."

    def test_update_product_not_reserved(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['pathParameters'] = {"productid": "12345678-prod-0002-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
        response = update_reservation.update_reserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No reserved item exists with this ID.", "Error was not as expected"

    def test_update_product_not_reserved_by_requestor(self, monkeypatch, dynamodb_mock, api_gateway_event):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0001-1234-abcdefghijkl"
        response = update_reservation.update_reserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "No reserved item exists with this ID.", "Error was not as expected"

    def test_update_product_with_wrong_quantities(self, monkeypatch, dynamodb_mock, api_gateway_event):
        api_gateway_event['pathParameters'] = {"productid": "12345678-prod-0002-1234-abcdefghijkl", "id": "12345678-list-0002-1234-abcdefghijkl"}
        api_gateway_event['body'] = "{\n    \"quantity\": 1\n}"
        api_gateway_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"

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
        response = update_reservation.update_reserve_main(api_gateway_event)
        body = json.loads(response['body'])
        assert body['error'] == "Reserved quantity for product (0) could not be updated by -1.", "Error was not as expected"
