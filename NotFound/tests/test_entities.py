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


@pytest.fixture()
def response_item_all():
    response_item = {
        "productId": {'S': "12345678-notf-0020-1234-abcdefghijkl"},
        "brand": {'S': "The White Company"},
        "details": {'S': "Halden Champagne Flutes – Set Of 4"},
        "productUrl": {'S': "https://www.thewhitecompany.com/uk/Halden-Champagne-Flutes--Set-of-4/p/GWHSC"},
        "imageUrl": {'S': "https://whitecompany.scene7.com/is/image/whitecompany/Halden-Champagne-Flutes---Set-of-4/GWHSC_2_MAIN?$D_PDP_412x412$"},
        "price": {'S': "40.00"}
    }

    return response_item


class TestProduct:
    def test_get_details(self, response_item):
        product = Product(response_item).get_details()
        assert product == {
            'productId': '12345678-notf-0010-1234-abcdefghijkl',
            'brand': 'John Lewis',
            'details': 'John Lewis & Partners Safari Mobile',
            'productUrl': 'https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165'
        }, "Object was not as expected."

    def test_get_all_details(self, response_item_all):
        product = Product(response_item_all).get_details()
        assert product == {
            'productId': '12345678-notf-0020-1234-abcdefghijkl',
            'brand': 'The White Company',
            'details': 'Halden Champagne Flutes – Set Of 4',
            'productUrl': 'https://www.thewhitecompany.com/uk/Halden-Champagne-Flutes--Set-of-4/p/GWHSC',
            'imageUrl': 'https://whitecompany.scene7.com/is/image/whitecompany/Halden-Champagne-Flutes---Set-of-4/GWHSC_2_MAIN?$D_PDP_412x412$',
            'price': '40.00'
        }, "Object was not as expected."
