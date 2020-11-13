import pytest
from products.entities import Product


@pytest.fixture()
def response_item():
    response_item = {
        "productId": {'S': "12345678-prod-0001-1234-abcdefghijkl"},
        "brand": {'S': "BABYBJÖRN"},
        "details": {'S': "Travel Cot Easy Go, Anthracite, with transport bag"},
        "imageUrl": {'S': "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg"},
        "productUrl": {'S': "https://www.amazon.co.uk/dp/B01H24LM58"},
        "price": {'S': "100.00"},
        "retailer": {'S': "amazon.co.uk"}
    }

    return response_item


class TestProduct:
    def test_get_details(self, response_item):
        product = Product(response_item).get_details()

        assert product['productId'] == '12345678-prod-0001-1234-abcdefghijkl', "Product ID was not as expected."
        assert product['brand'] == 'BABYBJÖRN', "Product brand not as expected."
        assert product['details'] == 'Travel Cot Easy Go, Anthracite, with transport bag', "Product details were not as expected."
        assert product['imageUrl'] == 'https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg', "Product url not as expected."
        assert product['productUrl'] == 'https://www.amazon.co.uk/dp/B01H24LM58', "Product url not as expected."
        assert product['price'] == '100.00', "Product price not as expected."
        assert product['retailer'] == 'amazon.co.uk', "Product price not as expected."
