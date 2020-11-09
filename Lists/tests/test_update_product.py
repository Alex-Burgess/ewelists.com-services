import pytest
import os
import re
import json
import boto3
from lists import update_product, logger

log = logger.setup_test_logger()


class TestUpdateExpression:
    def test_update_quantity(self):
        expression = update_product.update_expression(1, None)
        assert expression == "set quantity = :q"

    def test_update_notes(self):
        expression = update_product.update_expression(1, "Some notes")
        assert expression == "set quantity = :q, notes = :n"


class TestExpressionAttributeValues:
    def test_update_quantity(self):
        expression_values = update_product.expression_attribute_values(1, None)
        assert expression_values == {
            ':q': {'N': '1'}
        }

    def test_update_notes(self):
        expression_values = update_product.expression_attribute_values(1, "Some notes")
        assert expression_values == {
            ':q': {'N': '1'},
            ':n': {'S': "Some notes"}
        }


class TestUpdateProductItem:
    def test_update_product_item(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        updated_attributes = update_product.update_product_item('lists-unittest', list_id, product_id, 4, None)
        assert updated_attributes['quantity'] == 4, "Updated quantity was not 4."

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        assert test_response['Item']['quantity']['N'] == '4', "Quantity not as expected."

    def test_update_product_item_with_notes(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        updated_attributes = update_product.update_product_item('lists-unittest', list_id, product_id, 4, "Some custom note")
        assert updated_attributes['quantity'] == 4, "Updated quantity was not 4."
        assert updated_attributes['notes'] == "Some custom note", "Updated quantity was not 4."

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        assert test_response['Item']['quantity']['N'] == '4', "Quantity not as expected."

    def test_update_product_item_with_no_table(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            update_product.update_product_item('lists-unittes', list_id, product_id, 1, None)
        assert str(e.value) == "No table found", "Exception not as expected."


class TestUpdateProductMain:
    def test_update_product(self, api_update_product_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = update_product.update_product_main(api_update_product_event)
        body = json.loads(response['body'])
        assert body['quantity'] == 4, "Update to product quantity was not expected result."

    def test_update_product_with_notes(self, api_update_product_with_notes_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = update_product.update_product_main(api_update_product_with_notes_event)
        body = json.loads(response['body'])
        assert body['quantity'] == 4, "Update to product quantity was not expected result."
        assert body['notes'] == "Some custom user notes added", "Update to product notes was not expected result."

    def test_update_product_with_no_quantity(self, api_update_product_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_update_product_event['body'] = ''
        response = update_product.update_product_main(api_update_product_event)
        body = json.loads(response['body'])
        assert body['error'] == "Body was missing required attributes.", "Error not as expected."

    def test_update_product_with_not_owner(self, api_update_product_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_update_product_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"
        response = update_product.update_product_main(api_update_product_event)
        body = json.loads(response['body'])
        assert body['error'] == "User 12345678-user-0003-1234-abcdefghijkl was not owner of List 12345678-list-0001-1234-abcdefghijkl.", "Error not as expected."

    def test_add_product_with_no_list_id(self, api_update_product_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_update_product_event['pathParameters']['id'] = '12345678-list-0200-1234-abcdefghijkl'
        response = update_product.update_product_main(api_update_product_event)
        body = json.loads(response['body'])
        assert body['error'] == "List 12345678-list-0200-1234-abcdefghijkl does not exist.", "Error not as expected."

    def test_add_product_with_no_product_id(self, api_update_product_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_update_product_event['pathParameters']['productid'] = 'null'
        response = update_product.update_product_main(api_update_product_event)
        body = json.loads(response['body'])
        assert body['error'] == "Path contained a null productid parameter.", "Error not as expected."


def test_handler(api_update_product_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = update_product.handler(api_update_product_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    assert re.match('{"quantity": .*}', response['body']), "Response body was not as expected."
