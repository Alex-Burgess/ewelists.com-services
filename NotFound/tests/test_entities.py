import pytest
from notfound.entities import Product


@pytest.fixture()
def response_item():
    response_item = {
        "productId": {'S': "12345678-notf-0010-1234-abcdefghijkl"},
        "brand": {'S': "John Lewis"},
        "details": {'S': "John Lewis & Partners Safari Mobile"},
        "productUrl": {'S': "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"}
    }

    return response_item


class TestProduct:
    def test_get_details(self, response_item):
        product = Product(response_item).get_details()

        assert product['productId'] == '12345678-notf-0010-1234-abcdefghijkl', "Product ID was not as expected."
        assert product['brand'] == 'John Lewis', "Product brand not as expected."
        assert product['details'] == 'John Lewis & Partners Safari Mobile', "Product details were not as expected."
        assert product['productUrl'] == 'https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165', "Product url not as expected."
