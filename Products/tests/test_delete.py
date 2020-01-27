import pytest
import os
import json
import boto3
from moto import mock_dynamodb2
from products import delete
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
    event['resource'] = "/products/{id}"
    event['path'] = "/products/12345678-prod-0010-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"id": "12345678-prod-0010-1234-abcdefghijkl"}

    return event


@pytest.fixture
def dynamodb_mock():
    table_name = 'products-unittest'

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
        {"productId": "12345678-prod-0010-1234-abcdefghijkl", "retailer": "amazon", "brand": "BABYBJÖRN", "details": "Travel Cot Easy Go, Anthracite, with transport bag", "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58", "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg"},
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestDeleteProduct:
    def test_delete_product(self, dynamodb_mock):
        product_id = '12345678-prod-0010-1234-abcdefghijkl'
        result = delete.delete_product('products-unittest', product_id)
        assert result, "Delete result was not true"

    def test_delete_product_not_present(self, dynamodb_mock):
        # Result is true even if product doesn't exist from boto3.
        product_id = '12345678-prod-0011-1234-abcdefghijkl-bad'
        result = delete.delete_product('products-unittest', product_id)
        assert result, "Delete result was not true"


def test_handler(api_gateway_delete_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')
    response = delete.handler(api_gateway_delete_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    body = json.loads(response['body'])
    assert body['deleted'], "Response body was not as expected."
