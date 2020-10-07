import pytest
import os
import re
import json
import copy
from products import create

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestGetProductInfo:
    def test_get_product_info(self, api_create_event):
        product_info = create.get_product_info(api_create_event)
        assert product_info['retailer'] == "amazon.co.uk", "Attribute was not as expected."
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
    def test_put_product(self, empty_table):
        product_info = {
            "retailer": "amazon.co.uk",
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg"
        }

        product_id = create.put_product('products-unittest', product_info)
        assert len(product_id) == 36, 'Product ID not expected length.'

    def test_bad_table_name_throws_exception(self, empty_table):
        product_info = {
            "retailer": "amazon.co.uk",
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg"
        }

        with pytest.raises(Exception) as e:
            create.put_product('products-unittes', product_info)
        assert str(e.value) == "Product could not be created.", "Exception not as expected."


class TestCreateMain:
    def test_create_main(self, monkeypatch, api_create_event, empty_table):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')

        response = create.create_main(api_create_event)
        body = json.loads(response['body'])

        assert len(body['productId']) == 36, "Create main response did not contain a listId."

    def test_create_with_price(self, monkeypatch, api_create_with_price_event, empty_table):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')

        response = create.create_main(api_create_with_price_event)
        body = json.loads(response['body'])

        assert len(body['productId']) == 36, "Create main response did not contain a listId."

    def test_with_no_event_body(self, monkeypatch, api_create_event, empty_table):
        event_no_body = copy.deepcopy(api_create_event)
        event_no_body['body'] = None
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')

        response = create.create_main(event_no_body)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event did not contain a valid body.', "Create main response did not contain the correct error message."


def test_handler(api_create_event, monkeypatch, empty_table):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')
    response = create.handler(api_create_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"productId": .*}', response['body'])
