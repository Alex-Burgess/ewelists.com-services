class Product:

    def __init__(self, item):
        self.productId = item.get('productId').get('S')
        self.brand = item.get('brand').get('S')
        self.details = item.get('details').get('S')
        self.productUrl = item.get('productUrl').get('S')
        if item.get('price'):
            self.price = item.get('price').get('S')
        if item.get('imageUrl'):
            self.imageUrl = item.get('imageUrl').get('S')

    def __repr__(self):
        return "Product<{} -- {} -- {} -- {}>".format(self.productId, self.brand, self.details, self.productUrl)

    def get_details(self):
        product = {
            'productId': self.productId,
            'brand': self.brand,
            'details': self.details,
            'productUrl': self.productUrl
        }

        if hasattr(self, 'price'):
            product['price'] = self.price

        if hasattr(self, 'imageUrl'):
            product['imageUrl'] = self.imageUrl

        return product
