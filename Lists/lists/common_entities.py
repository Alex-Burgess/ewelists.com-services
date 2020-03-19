class User:

    def __init__(self, item):
        self.user_id = item.get('userId').get('S')
        self.email = item.get('email').get('S')
        if item.get('name'):
            self.name = item.get('name').get('S')

    def __repr__(self):
        return "User<{} -- {} -- {}>".format(self.username, self.name, self.email)

    def get_basic_details(self):
        user = {
            'email': self.email,
            'userId': self.user_id
        }

        if hasattr(self, 'name'):
            user['name'] = self.name
        else:
            user['name'] = self.email

        return user


class List:

    def __init__(self, item):
        self.listId = item.get('listId').get('S')
        self.title = item.get('title').get('S')
        self.description = item.get('description').get('S')
        self.occasion = item.get('occasion').get('S')
        self.imageUrl = item.get('imageUrl').get('S')
        self.listOwner = item.get('listOwner').get('S')
        self.state = item.get('state').get('S')
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
            'imageUrl': self.imageUrl,
            'listOwner': self.listOwner,
            'state': self.state
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
        self.purchased = item.get('purchased').get('N')
        self.type = item.get('type').get('S')

    def __repr__(self):
        return "Product<{} -- {} -- {} -- {}>".format(self.productId, self.listId, self.quantity, self.reserved, self.type)

    def get_details(self):
        product = {
            'productId': self.productId,
            'quantity': int(self.quantity),
            'reserved': int(self.reserved),
            'purchased': int(self.purchased),
            'type': self.type
        }

        return product


class Reserved:
    def __init__(self, item):
        self.listId = item.get('PK').get('S')
        self.productId = item.get('productId').get('S')
        self.quantity = item.get('quantity').get('N')
        self.name = item.get('name').get('S')
        self.userId = item.get('userId').get('S')
        self.reservationId = item.get('reservationId').get('S')
        if item.get('state'):
            self.state = item.get('state').get('S')
        if item.get('message'):
            self.message = item.get('message').get('S')

    def __repr__(self):
        return "Reserved<{} -- {} -- {} -- {} -- {} -- {}>".format(self.productId, self.listId, self.quantity, self.name, self.userId, self.message)

    def get_details(self):
        reserved = {
            'productId': self.productId,
            'quantity': int(self.quantity),
            'name': self.name,
            'userId': self.userId,
            'reservationId': self.reservationId
        }

        if hasattr(self, 'state'):
            reserved['state'] = self.state

        if hasattr(self, 'message'):
            reserved['message'] = self.message

        return reserved


class Reservation:
    def __init__(self, item):
        self.reservationId = item.get('reservationId').get('S')
        self.userId = item.get('userId').get('S')
        self.name = item.get('name').get('S')
        self.email = item.get('email').get('S')
        self.listId = item.get('listId').get('S')
        self.title = item.get('title').get('S')
        self.productId = item.get('productId').get('S')
        self.productType = item.get('productType').get('S')
        self.quantity = item.get('quantity').get('N')
        self.state = item.get('state').get('S')

    def __repr__(self):
        return "Reservation<{}>".format(self.reservationId)

    def get_details(self):
        reserved = {
            'reservationId': self.reservationId,
            'userId': self.userId,
            'name': self.name,
            'email': self.email,
            'listId': self.listId,
            'title': self.title,
            'productId': self.productId,
            'productType': self.productType,
            'quantity': int(self.quantity),
            'state': self.state
        }

        return reserved
