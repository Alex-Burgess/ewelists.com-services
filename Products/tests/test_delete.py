import os
import json
from products import delete

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestDeleteProduct:
    def test_delete_product(self, table):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        result = delete.delete_product('products-unittest', product_id)
        assert result, "Delete result was not true"

    def test_delete_product_not_present(self, table):
        # Result is true even if product doesn't exist from boto3.
        product_id = '12345678-prod-0011-1234-abcdefghijkl-bad'
        result = delete.delete_product('products-unittest', product_id)
        assert result, "Delete result was not true"


def test_handler(api_gateway_delete_event, monkeypatch, table):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')
    response = delete.handler(api_gateway_delete_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    body = json.loads(response['body'])
    assert body['deleted'], "Response body was not as expected."
