import pytest
import os
import json
from notfound import delete
import sys
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestDeleteProduct:
    def test_delete_product(self, table):
        cognito_user_id = '12345678-user-0001-1234-abcdefghijkl'
        product_id = '12345678-notf-0010-1234-abcdefghijkl'
        result = delete.delete_product('notfound-unittest', cognito_user_id, product_id)
        assert result, "Delete result was not true"

    def test_delete_product_not_present(self, table):
        cognito_user_id = '12345678-user-0001-1234-abcdefghijkl'
        product_id = '12345678-notf-0011-1234-abcdefghijkl-bad'

        with pytest.raises(Exception) as e:
            delete.delete_product('notfound-unittest', cognito_user_id, product_id)
        assert str(e.value) == "Product can not be deleted.", "Exception not as expected."

    def test_delete_product_not_createdby_user(self, table):
        cognito_user_id = '12345678-user-0002-1234-abcdefghijkl'
        product_id = '12345678-notf-0010-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete.delete_product('notfound-unittest', cognito_user_id, product_id)
        assert str(e.value) == "Product can not be deleted.", "Exception not as expected."


def test_handler(api_gateway_delete_event, monkeypatch, table):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')
    response = delete.handler(api_gateway_delete_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    body = json.loads(response['body'])
    assert body['deleted'], "Response body was not as expected."
