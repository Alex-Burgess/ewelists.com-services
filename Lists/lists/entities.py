class User:

    def __init__(self, item):
        self.user_id = item.get('userId').get('S')
        self.name = item.get('name').get('S')
        self.email = item.get('email').get('S')

    def __repr__(self):
        return "User<{} -- {} -- {}>".format(self.username, self.name, self.email)

    def get_basic_details(self):
        user = {
            'name': self.name,
            'email': self.email
        }

        return user


class List:

    def __init__(self, item):
        self.listId = item.get('listId').get('S')
        self.title = item.get('title').get('S')
        self.description = item.get('description').get('S')
        self.occasion = item.get('occasion').get('S')
        self.eventDate = item.get('eventDate').get('S')

    def __repr__(self):
        return "List<{} -- {} -- {}>".format(self.list_id, self.title, self.occasion)

    def get_details(self):
        list = {
            'listId': self.listId,
            'title': self.title,
            'description': self.description,
            'occasion': self.occasion,
            'eventDate': self.eventDate
        }

        return list


class Product:

    def __init__(self, item):
        self.product_id = item.get('PK').get('S')
        self.list_id = item.get('SK').get('S')
        # self.description = item.get('description').get('S')
        self.quantity = item.get('quantity').get('S')
        self.reserved = item.get('reserved').get('S')

    def __repr__(self):
        return "Product<{} -- {} -- {} -- {}>".format(self.product_id, self.list_id, self.quantity, self.reserved)
