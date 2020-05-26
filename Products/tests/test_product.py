import pytest
import os
import re
import json
import boto3
from decimal import Decimal
from moto import mock_dynamodb2
from products import product
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_get_product_event():
    event = fixtures.api_gateway_base_event()
    event['resource'] = "/products/{id}"
    event['path'] = "/products/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-prod-0001-1234-abcdefghijkl"}
    event['body'] = "null"

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
        {
            "productId": "12345678-prod-0001-1234-abcdefghijkl",
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "price": "100.00"
        },
        {
            "productId": "12345678-prod-0002-1234-abcdefghijkl",
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58"
        }
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetProduct:
    def test_get_product(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        product_object = product.get_product('products-unittest', product_id)
        assert product_object['brand'] == "BABYBJÖRN", "Attribute brand was not as expected."
        assert product_object['details'] == "Travel Cot Easy Go, Anthracite, with transport bag", "Attribute details was not as expected."
        assert product_object['imageUrl'] == "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg", "Attribute url was not as expected."
        assert product_object['productUrl'] == "https://www.amazon.co.uk/dp/B01H24LM58", "Attribute url was not as expected."
        assert product_object['price'] == "100.00", "Attribute price was not as expected."

    def test_get_product_no_price(self, dynamodb_mock):
        product_id = '12345678-prod-0002-1234-abcdefghijkl'
        product_object = product.get_product('products-unittest', product_id)
        assert product_object['brand'] == "BABYBJÖRN", "Attribute brand was not as expected."
        assert product_object['details'] == "Travel Cot Easy Go, Anthracite, with transport bag", "Attribute details was not as expected."
        assert product_object['imageUrl'] == "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg", "Attribute url was not as expected."
        assert product_object['productUrl'] == "https://www.amazon.co.uk/dp/B01H24LM58", "Attribute url was not as expected."
        assert 'price' not in product_object, "Attribute price was not as expected."

    def test_with_missing_product_id(self, dynamodb_mock):
        product_id = '12345678-notf-0011-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            product.get_product('products-unittest', product_id)
        assert str(e.value) == "No product exists with this ID.", "Exception not as expected."

    def test_with_bad_table(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            product.get_product('notfound-unittes', product_id)
        assert str(e.value) == "Unexpected problem getting product from table.", "Exception not as expected."


class TestGetMain:
    def test_get_main(self, monkeypatch, api_gateway_get_product_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')
        response = product.get_main(api_gateway_get_product_event)
        body = json.loads(response['body'])
        assert body['productId'] == '12345678-prod-0001-1234-abcdefghijkl', "product Id was not as expected."

    def test_with_missing_product_id(self, monkeypatch, api_gateway_get_product_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')
        api_gateway_get_product_event['pathParameters']['id'] = '12345678-notf-0011-1234-abcdefghijkl'

        response = product.get_main(api_gateway_get_product_event)
        body = json.loads(response['body'])
        assert body['error'] == 'No product exists with this ID.', "Create main response did not contain the correct error message."


def test_handler(api_gateway_get_product_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')
    response = product.handler(api_gateway_get_product_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"productId": .*}', response['body'])
