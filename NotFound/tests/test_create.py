import pytest
import os
import re
import json
import copy
from notfound import create

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestGetProductInfo:
    def test_get_product_info(self, api_gateway_create_event):
        product_info = create.get_product_info(api_gateway_create_event)
        assert product_info['brand'] == "BABYBJÖRN", "Attribute brand was not as expected."
        assert product_info['details'] == "Travel Cot Easy Go, Anthracite, with transport bag", "Attribute details was not as expected."
        assert product_info['url'] == "https://www.amazon.co.uk/dp/B01H24LM58", "Attribute url was not as expected."

    def test_with_empty_body_throws_exception(self, api_gateway_create_event):
        event_no_body = copy.deepcopy(api_gateway_create_event)
        event_no_body['body'] = None

        with pytest.raises(Exception) as e:
            create.get_product_info(event_no_body)
        assert str(e.value) == "API Event did not contain a valid body.", "Exception not as expected."


class TestPutProduct:
    def test_put_product(self, table):
        cognito_user_id = '12345678-user-0001-1234-abcdefghijkl'
        product_info = {
            'brand': 'Mamas & Papas',
            'details': 'Hilston Nursing Chair - Silver',
            'url': 'https://www.mamasandpapas.com/en-gb/hilston-nursing-chair-duck-egg/p/chnsoa100',
        }

        product_id = create.put_product('notfound-unittest', cognito_user_id, product_info)
        assert len(product_id) == 36, 'Product ID not expected length.'

    def test_bad_table_name_throws_exception(self, table):
        cognito_user_id = '12345678-user-0001-1234-abcdefghijkl'
        product_info = {
            'brand': 'Mamas & Papas',
            'details': 'Hilston Nursing Chair - Silver',
            'url': 'https://www.mamasandpapas.com/en-gb/hilston-nursing-chair-duck-egg/p/chnsoa100',
        }

        with pytest.raises(Exception) as e:
            create.put_product('notfound-unittes', cognito_user_id, product_info)
        assert str(e.value) == "Product could not be created.", "Exception not as expected."


class TestCreateMain:
    def test_create_main(self, monkeypatch, api_gateway_create_event, table):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')

        response = create.create_main(api_gateway_create_event)
        body = json.loads(response['body'])

        assert len(body['productId']) == 36, "Create main response did not contain a listId."

    def test_with_no_event_body(self, monkeypatch, api_gateway_create_event, table):
        event_no_body = copy.deepcopy(api_gateway_create_event)
        event_no_body['body'] = None
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')

        response = create.create_main(event_no_body)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event did not contain a valid body.', "Create main response did not contain the correct error message."


def test_handler(api_gateway_create_event, monkeypatch, table):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')
    response = create.handler(api_gateway_create_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"productId": .*}', response['body'])
