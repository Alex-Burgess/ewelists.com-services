import pytest
import os
import re
import json
import copy
import boto3
from moto import mock_dynamodb2
from products import create
from tests import fixtures

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_create_event():
    event = fixtures.api_gateway_base_event()
    event['httpMethod'] = "POST"
    event['body'] = "{\n    \"retailer\": \"amazon\",\n    \"brand\": \"BABYBJÖRN\",\n    \"details\": \"Travel Cot Easy Go, Anthracite, with transport bag\",\n    \"productUrl\": \"https://www.amazon.co.uk/dp/B01H24LM58\",\n    \"imageUrl\": \"https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg\"\n}"

    return event


@pytest.fixture
def api_create_with_price_event():
    event = fixtures.api_gateway_base_event()
    event['httpMethod'] = "POST"
    event['body'] = "{\n    \"retailer\": \"amazon\",\n    \"price\": \"100.00\",\n    \"brand\": \"BABYBJÖRN\",\n    \"details\": \"Travel Cot Easy Go, Anthracite, with transport bag\",\n    \"productUrl\": \"https://www.amazon.co.uk/dp/B01H24LM58\",\n    \"imageUrl\": \"https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg\"\n}"

    return event


@pytest.fixture
def dynamodb_mock():
    table_name = 'products-unittest'

    mock = mock_dynamodb2()
    mock.start()

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
    )

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetProductInfo:
    def test_get_product_info(self, api_create_event):
        product_info = create.get_product_info(api_create_event)
        assert product_info['retailer'] == "amazon", "Attribute was not as expected."
        assert product_info['brand'] == "BABYBJÖRN", "Attribute was not as expected."
        assert product_info['details'] == "Travel Cot Easy Go, Anthracite, with transport bag", "Attribute was not as expected."
        assert product_info['productUrl'] == "https://www.amazon.co.uk/dp/B01H24LM58", "Attribute was not as expected."
        assert product_info['imageUrl'] == "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg", "Attribute was not as expected."

    def test_with_empty_body_throws_exception(self, api_create_event):
        event_no_body = copy.deepcopy(api_create_event)
        event_no_body['body'] = None

        with pytest.raises(Exception) as e:
            create.get_product_info(event_no_body)
        assert str(e.value) == "API Event did not contain a valid body.", "Exception not as expected."


class TestPutProduct:
    def test_put_product(self, dynamodb_mock):
        product_info = {
            "retailer": "amazon",
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg"
        }

        product_id = create.put_product('products-unittest', product_info)
        assert len(product_id) == 36, 'Product ID not expected length.'

    def test_bad_table_name_throws_exception(self, dynamodb_mock):
        product_info = {
            "retailer": "amazon",
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg"
        }

        with pytest.raises(Exception) as e:
            create.put_product('products-unittes', product_info)
        assert str(e.value) == "Product could not be created.", "Exception not as expected."


class TestCreateMain:
    def test_create_main(self, monkeypatch, api_create_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')

        response = create.create_main(api_create_event)
        body = json.loads(response['body'])

        assert len(body['productId']) == 36, "Create main response did not contain a listId."

    def test_create_with_price(self, monkeypatch, api_create_with_price_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')

        response = create.create_main(api_create_with_price_event)
        body = json.loads(response['body'])

        assert len(body['productId']) == 36, "Create main response did not contain a listId."

    def test_with_no_event_body(self, monkeypatch, api_create_event, dynamodb_mock):
        event_no_body = copy.deepcopy(api_create_event)
        event_no_body['body'] = None
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')

        response = create.create_main(event_no_body)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event did not contain a valid body.', "Create main response did not contain the correct error message."


def test_handler(api_create_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')
    response = create.handler(api_create_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"productId": .*}', response['body'])
