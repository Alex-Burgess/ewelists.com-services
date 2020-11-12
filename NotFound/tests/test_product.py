import pytest
import os
import re
import json
from notfound import product
import sys
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestGetProduct:
    def test_get_product(self, table):
        product_id = '12345678-notf-0010-1234-abcdefghijkl'
        product_object = product.get_product('notfound-unittest', product_id)
        assert product_object == {
            'productId': '12345678-notf-0010-1234-abcdefghijkl',
            'brand': 'John Lewis',
            'details': 'John Lewis & Partners Safari Mobile',
            'productUrl': 'https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165'
        }, "Object was not as expected."

    def test_get_product_with_full_details(self, table):
        product_id = '12345678-notf-0020-1234-abcdefghijkl'
        product_object = product.get_product('notfound-unittest', product_id)
        assert product_object == {
            'productId': '12345678-notf-0020-1234-abcdefghijkl',
            'brand': 'The White Company',
            'details': 'Halden Champagne Flutes – Set Of 4',
            'productUrl': 'https://www.thewhitecompany.com/uk/Halden-Champagne-Flutes--Set-of-4/p/GWHSC',
            'imageUrl': 'https://whitecompany.scene7.com/is/image/whitecompany/Halden-Champagne-Flutes---Set-of-4/GWHSC_2_MAIN?$D_PDP_412x412$',
            'price': '40.00'
        }, "Object was not as expected."

    def test_with_missing_product_id(self, table):
        product_id = '12345678-notf-0011-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            product.get_product('notfound-unittest', product_id)
        assert str(e.value) == "No product exists with this ID.", "Exception not as expected."

    def test_with_bad_table(self, table):
        product_id = '12345678-notf-0010-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            product.get_product('notfound-unittes', product_id)
        assert str(e.value) == "Unexpected problem getting product from table.", "Exception not as expected."


class TestGetMain:
    def test_get_main(self, monkeypatch, api_gateway_get_product_event, table):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')
        response = product.get_main(api_gateway_get_product_event)
        body = json.loads(response['body'])
        assert body['productId'] == '12345678-notf-0010-1234-abcdefghijkl', "product Id was not as expected."

    def test_with_missing_product_id(self, monkeypatch, api_gateway_get_product_event, table):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')
        api_gateway_get_product_event['pathParameters']['id'] = '12345678-notf-0011-1234-abcdefghijkl'

        response = product.get_main(api_gateway_get_product_event)
        body = json.loads(response['body'])
        assert body['error'] == 'No product exists with this ID.', "Create main response did not contain the correct error message."


def test_handler(api_gateway_get_product_event, monkeypatch, table):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')
    response = product.handler(api_gateway_get_product_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"productId": .*}', response['body'])
