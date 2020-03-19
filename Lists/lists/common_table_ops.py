import boto3
from lists import logger
from lists.common_entities import List, Product, Reserved
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
        print(e.response['Error']['Message'])

    if 'Item' not in response:
        log.info("No items for the list {} were found.".format(list_id))
        raise Exception("No list exists with this ID.")

    return response['Item']


def get_list_owner_item(table_name, list_id):
    log.info("Querying table {} to find all items associated with list id {}".format(table_name, list_id))

    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        log.info("All items in query response. ({})".format(response['Items']))
    except Exception as e:
        log.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting list items from table.")

    if len(response['Items']) == 0:
        log.info("No items for the list {} were found.".format(list_id))
        raise Exception("No list exists with this ID.")

    for item in response['Items']:
        if item['SK']['S'].startswith("USER"):
            return List(item).get_details()


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

    user = {
        'email': response['Item']['email']['S'],
        'name': response['Item']['name']['S']
    }

    return user


def does_user_have_account(table_name, index_name, email):
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


def get_reserved_details_item(table_name, list_id, product_id, user_id):
    key = {
        'PK': {'S': "LIST#" + list_id},
        'SK': {'S': "RESERVED#" + product_id + "#" + user_id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        log.info("Get reserved item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    if 'Item' not in response:
        log.info("No reserved details were found for list {} and product id {} was found.".format(list_id, product_id))
        raise Exception("Product is not reserved by user.")

    item = response['Item']
    log.info("Reserved Item: {}".format(item))

    return Reserved(item).get_details()


def check_product_not_reserved_by_user(table_name, list_id, product_id, user_id):
    key = {
        'PK': {'S': "LIST#" + list_id},
        'SK': {'S': "RESERVED#" + product_id + "#" + user_id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        log.info("Get reserved item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    if 'Item' in response:
        log.info("Reserved product was found for list {}, product id {} and user {}.".format(list_id, product_id, user_id))
        raise Exception("Product already reserved by user.")

    return True
