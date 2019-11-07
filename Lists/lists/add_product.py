import json
import os
import boto3
import logging
from lists import common
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    logger.info("event:" + json.dumps(event))
    response = add_product_main(event)
    return response


def add_product_main(event):
    table_name = common.get_table_name(os.environ)
    identity = common.get_identity(event, os.environ)
    list_id = common.get_list_id(event)
    product_id = common.get_product_id(event)
    quantity = common.get_product_id(event)
    type = "products"       # Add method that gets this from body.  Type can only be products or notfound.

    list_item = get_list(table_name, identity['userPoolSub'], list_id)

    common.confirm_owner(identity['userPoolSub'], list_id, list_item)

    message = create_product_item(table_name, list_id, product_id, type, quantity)

    data = {'message': message}
    response = common.create_response(200, json.dumps(data))
    return response


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


def create_product_item(table_name, list_id, product_id, type, quantity):
    item = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)},
        'type': {'S': type},
        'quantity': {'N': str(quantity)},
        'reserved': {'N': str(0)}
    }

    try:
        logger.info("Put product item: {}".format(item))
        dynamodb.put_item(TableName=table_name, Item=item)
    except Exception as e:
        logger.error("Product could not be created: {}".format(e))
        raise Exception('Product could not be created.')

    return True
