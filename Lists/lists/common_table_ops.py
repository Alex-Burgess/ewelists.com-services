import boto3
import logging
from lists.common_entities import Product, Reserved
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


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
        logger.info("Get list item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    if 'Item' not in response:
        logger.info("No items for the list {} were found.".format(list_id))
        raise Exception("No list exists with this ID.")

    return response['Item']


def get_users_name(table_name, user_id):
    key = {
        'PK': {'S': "USER#" + user_id},
        'SK': {'S': "USER#" + user_id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        logger.info("Get user item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    if 'Item' not in response:
        logger.info("No user id {} was found.".format(user_id))
        raise Exception("No user exists with this ID.")

    if 'name' not in response['Item']:
        return response['Item']['email']['S']

    return response['Item']['name']['S']


def get_product_item(table_name, list_id, product_id):
    logger.info("Getting product item {} for list {}.".format(product_id, list_id))
    key = {
        'PK': {'S': "LIST#" + list_id},
        'SK': {'S': "PRODUCT#" + product_id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        logger.info("Get product item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    if 'Item' not in response:
        logger.info("No product was found for list {} and product id {} was found.".format(list_id, product_id))
        raise Exception("No product item exists with this ID.")

    item = response['Item']
    logger.info("Product Item: {}".format(item))

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
        logger.info("Get reserved item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    if 'Item' not in response:
        logger.info("No reserved details were found for list {} and product id {} was found.".format(list_id, product_id))
        raise Exception("No reserved item exists with this ID.")

    item = response['Item']
    logger.info("Reserved Item: {}".format(item))

    return Reserved(item).get_details()
