import pytest
import os
from products import common

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


def test_create_response():
    response = common.create_response(200, 'Success message')

    expected_response = {'statusCode': 200,
                         'body': 'Success message',
                         'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                         }}
    assert response == expected_response, "Create_response did not return the expected response value."


class TestGetTableName:
    def test_get_table_name(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-test')
        table_name = common.get_table_name(os.environ)
        assert table_name == "products-test", "Table name from os environment variables was not as expected."

    def test_get_table_name_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_table_name(os.environ)
        assert str(e.value) == "TABLE_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetTableIndex:
    def test_get_table_index(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'index-test')
        index_name = common.get_table_index(os.environ)
        assert index_name == "index-test", "Index name from os environment variables was not as expected."

    def test_get_table_index_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_table_index(os.environ)
        assert str(e.value) == "INDEX_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetProductId:
    def test_get_product_id(self, api_gateway_with_id_event):
        product_id = common.get_product_id(api_gateway_with_id_event)
        assert product_id == "12345678-prod-0001-1234-abcdefghijkl", "Product ID returned from API event was not as expected."

    def test_product_id_not_present(self, api_gateway_event_with_no_product_id):
        with pytest.raises(Exception) as e:
            common.get_product_id(api_gateway_event_with_no_product_id)
        assert str(e.value) == "API Event did not contain a Product ID in the path parameters.", "Exception not as expected."
