import boto3
from lists import logger
from lists.common_entities import User, List, Product, Reservation
from botocore.exceptions import ClientError

log = logger.setup_logger()


dynamodb = boto3.client('dynamodb')


def get_list(table_name, cognito_user_id, list_id):
    key = {
        'PK': {'S': "LIST#" + list_id},
        'SK': {'S': "USER#" + cognito_user_id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        log.info("Get list item response: {}".format(response))
    except ClientError as e:
        raise Exception("Unexpected error: " + e.response['Error']['Message'])

    if 'Item' not in response:
        log.info("No items for the list {} were found.".format(list_id))
        raise Exception("No list exists with this ID.")

    return List(response['Item']).get_details()


def get_users_details(table_name, user_id):
    key = {
        'PK': {'S': "USER#" + user_id},
        'SK': {'S': "USER#" + user_id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        log.info("Get user item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    if 'Item' not in response:
        log.info("No user id {} was found.".format(user_id))
        raise Exception("No user exists with this ID.")

    return User(response['Item']).get_basic_details()


def get_user_id_from_email(table_name, index_name, email):
    try:
        response = dynamodb.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression="email = :email",
            ExpressionAttributeValues={":email":  {'S': email}}
        )
    except Exception as e:
        log.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting user from table.")

    for item in response['Items']:
        if item['PK']['S'].startswith("USER"):
            log.info("User with email {} was found.".format(email))
            return item['userId']['S']

    return False


def get_product_item(table_name, list_id, product_id):
    log.info("Getting product item {} for list {}.".format(product_id, list_id))
    key = {
        'PK': {'S': "LIST#" + list_id},
        'SK': {'S': "PRODUCT#" + product_id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        log.info("Get product item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    if 'Item' not in response:
        log.info("No product was found for list {} and product id {} was found.".format(list_id, product_id))
        raise Exception("No product item exists with this ID.")

    item = response['Item']
    log.info("Product Item: {}".format(item))

    return Product(item).get_details()


def get_reservation_items_query(table_name, list_id, product_id, user_id):
    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="PK = :PK and begins_with(SK, :SK)",
            ExpressionAttributeValues={
                ":PK":  {'S': "LIST#" + list_id},
                ":SK":  {'S': "RESERVATION#" + product_id + "#" + user_id}
            }
        )
        log.info("Get reserved item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    return response['Items']


def get_reservations(table_name, list_id, product_id, user_id):
    items = get_reservation_items_query(table_name, list_id, product_id, user_id)

    log.info("Items {}.".format(items))

    if len(items) == 0:
        log.info("No reserved details were found for list {} and product id {}.".format(list_id, product_id))
        raise Exception("Product is not reserved by user.")

    return_items = []
    for item in items:
        return_items.append(Reservation(item).get_details())

    return return_items


def check_product_not_reserved_by_user(table_name, list_id, product_id, user_id):
    log.info("Checking product not already reserved by user.")

    items = get_reservation_items_query(table_name, list_id, product_id, user_id)
    log.info("Items to check: {}.".format(items))

    if len(items) > 0:
        for item in items:
            if item['state']['S'] == 'reserved':
                raise Exception("Product already reserved by user.")

    return True


def get_reservation(table_name, index_name, resv_id):
    try:
        response = dynamodb.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression="reservationId = :reservationId",
            ExpressionAttributeValues={":reservationId":  {'S': resv_id}}
        )
    except Exception as e:
        log.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting user from table.")

    items = response['Items']
    log.info("Items returned {}.".format(items))

    if len(items) == 0:
        raise Exception("Reservation ID does not exist.")
    elif len(items) > 1:
        log.info("Multiple items were found with same reservation id {}.".format(resv_id))
        raise Exception("Multiple items were found with same reservation id.")

    return Reservation(items[0]).get_details()
