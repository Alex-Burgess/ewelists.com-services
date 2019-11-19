import json
import os
import boto3
import logging
from lists import common
from lists.entities import Product, Reserved
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = unreserve_main(event)
    return response


def unreserve_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        list_id = common.get_list_id(event)
        product_id = common.get_product_id(event)

        # Step 1 - get reserved item and product item.
        reserved_item = get_reserved_details_item(table_name, list_id, product_id)
        product_item = get_product_item(table_name, list_id, product_id)

        # Step 2 - Check that requestor id matches userid of reserved details.
        confirm_user_reserved_product(identity['userPoolSub'], reserved_item)

        # Step 3 - Calculate new reserved quantity of product.
        new_product_reserved_quantity = calculate_new_reserved_quantity(product_item, -reserved_item['quantity'])

        # Step 4 - Delete reserved details item and update product reserved quantities
        update_items(table_name, list_id, product_id, new_product_reserved_quantity)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'unreserved': 'true'}

    response = common.create_response(200, json.dumps(data))
    return response


def get_reserved_details_item(table_name, list_id, product_id):
    key = {
        'PK': {'S': "LIST#" + list_id},
        'SK': {'S': "RESERVED#PRODUCT#" + product_id}
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


def get_product_item(table_name, list_id, product_id):
    key = {
        'PK': {'S': "LIST#" + list_id},
        'SK': {'S': "PRODUCT#" + product_id}
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
        logger.info("No product was found for list {} and product id {} was found.".format(list_id, product_id))
        raise Exception("No product item exists with this ID.")

    item = response['Item']
    logger.info("Product Item: {}".format(item))

    return Product(item).get_details()


def confirm_user_reserved_product(user_id, reserved_item):
    if user_id != reserved_item['userId']:
        logger.info("Requestor ID {} did not match user id of reserved item user ID {}.".format(user_id, reserved_item['userId']))
        raise Exception("Requestor ID {} did not match user id of reserved item user ID {}.".format(user_id, reserved_item['userId']))

    return True


def calculate_new_reserved_quantity(product_item, update_amount):
    new_quantity = product_item['reserved'] + update_amount
    logger.info("Product reserved quantity updated from {} to {}".format(product_item['reserved'], new_quantity))

    if new_quantity < 0:
        logger.info("Reserved quantity for product ({}) could not be updated by {}.".format(product_item['reserved'], update_amount))
        raise Exception("Reserved quantity for product ({}) could not be updated by {}.".format(product_item['reserved'], update_amount))

    return new_quantity


def update_items(table_name, list_id, product_id, new_product_reserved_quantity):
    product_key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    reserved_key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "RESERVED#PRODUCT#{}".format(product_id)}
    }

    condition = {
        ':PK': {'S': "LIST#{}".format(list_id)},
        ':SK': {'S': "RESERVED#PRODUCT#{}".format(product_id)}
    }

    try:
        response = dynamodb.transact_write_items(
            TransactItems=[
                {
                    'Update': {
                        'TableName': table_name,
                        'Key': product_key,
                        'UpdateExpression': "set reserved = :r",
                        'ExpressionAttributeValues': {
                            ':r': {'N': str(new_product_reserved_quantity)},
                        }
                    }
                },
                {
                    'Delete': {
                        'TableName': table_name,
                        'Key': reserved_key,
                        'ConditionExpression': "PK = :PK AND SK = :SK",
                        'ExpressionAttributeValues': condition
                    }
                }
            ]
        )

        logger.info("Attributes updated: " + json.dumps(response))
    except Exception as e:
        logger.info("Transaction write exception: " + str(e))
        raise Exception("Unexpected error when unreserving product.")

    return True
