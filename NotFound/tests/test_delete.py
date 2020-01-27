import pytest
import os
import json
import boto3
from moto import mock_dynamodb2
from notfound import delete
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_delete_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/notfound/{id}"
    event['path'] = "/notfound/12345678-notf-0010-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"id": "12345678-notf-0010-1234-abcdefghijkl"}

    return event


@pytest.fixture
def dynamodb_mock():
    table_name = 'notfound-unittest'

    mock = mock_dynamodb2()
    mock.start()

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    items = [
        {"productId": "12345678-notf-0010-1234-abcdefghijkl", "brand": "John Lewis", "details": "John Lewis & Partners Safari Mobile", "productUrl": "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165", "createdBy": "12345678-user-0001-1234-abcdefghijkl"},
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestDeleteProduct:
    def test_delete_product(self, dynamodb_mock):
        cognito_user_id = '12345678-user-0001-1234-abcdefghijkl'
        product_id = '12345678-notf-0010-1234-abcdefghijkl'
        result = delete.delete_product('notfound-unittest', cognito_user_id, product_id)
        assert result, "Delete result was not true"

    # @pytest.mark.skip(reason="Moto is not throwing an exception when deleting with ConditionExpression")
    def test_delete_product_not_present(self, dynamodb_mock):
        cognito_user_id = '12345678-user-0001-1234-abcdefghijkl'
        product_id = '12345678-notf-0011-1234-abcdefghijkl-bad'

        with pytest.raises(Exception) as e:
            delete.delete_product('notfound-unittest', cognito_user_id, product_id)
        assert str(e.value) == "Product can not be deleted.", "Exception not as expected."

    # @pytest.mark.skip(reason="Moto is not throwing an exception when deleting with ConditionExpression")
    def test_delete_product_not_createdby_user(self, dynamodb_mock):
        cognito_user_id = '12345678-user-0002-1234-abcdefghijkl'
        product_id = '12345678-notf-0010-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete.delete_product('notfound-unittest', cognito_user_id, product_id)
        assert str(e.value) == "Product can not be deleted.", "Exception not as expected."


def test_handler(api_gateway_delete_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')
    response = delete.handler(api_gateway_delete_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    body = json.loads(response['body'])
    assert body['deleted'], "Response body was not as expected."
