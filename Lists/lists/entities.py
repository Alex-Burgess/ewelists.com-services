class User:

    def __init__(self, item):
        self.user_id = item.get('userId').get('S')
        # self.name = item.get('name').get('S')
        self.email = item.get('email').get('S')

    def __repr__(self):
        # return "User<{} -- {} -- {}>".format(self.username, self.name, self.email)
        return "User<{} -- {} -- {}>".format(self.username, self.email)

    def get_basic_details(self):
        user = {
            # 'name': self.name,
            'email': self.email
        }

        return user


class List:

    def __init__(self, item):
        self.listId = item.get('listId').get('S')
        self.title = item.get('title').get('S')
        self.description = item.get('description').get('S')
        self.occasion = item.get('occasion').get('S')
        self.imageUrl = item.get('imageUrl').get('S')
        if item.get('eventDate'):
            self.eventDate = item.get('eventDate').get('S')

    def __repr__(self):
        return "List<{} -- {} -- {}>".format(self.listId, self.title, self.occasion, self.imageUrl)

    def get_details(self):
        list = {
            'listId': self.listId,
            'title': self.title,
            'description': self.description,
            'occasion': self.occasion,
            'imageUrl': self.imageUrl
        }

        if hasattr(self, 'eventDate'):
            list['eventDate'] = self.eventDate

        return list


class Product:

    def __init__(self, item):
        self.listId = item.get('PK').get('S')
        self.productId = item.get('SK').get('S').split("#")[1]
        self.quantity = item.get('quantity').get('N')
        self.reserved = item.get('reserved').get('N')
        self.type = item.get('type').get('S')
        if item.get('reservedDetails'):
            self.reservedDetails = item.get('reservedDetails').get('L')

    def __repr__(self):
        return "Product<{} -- {} -- {} -- {}>".format(self.productId, self.listId, self.quantity, self.reserved, self.type)

    def get_details(self):
        product = {
            'productId': self.productId,
            'quantity': int(self.quantity),
            'reserved': int(self.reserved),
            'type': self.type
        }

        if hasattr(self, 'reservedDetails'):
            reserved_list = self.reservedDetails

            reserved_user_map = reserved_list[0].get('M') # loop

            user_map = {
                'name': reserved_user_map.get('name').get('S')
            }
            product['reservedDetails'] = [
                user_map
            ]

        return product
