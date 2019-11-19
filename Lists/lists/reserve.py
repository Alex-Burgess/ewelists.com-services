import json
import os
import boto3
import logging
import time
from lists import common
from lists import common_env_vars
from lists import common_event
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = reserve_main(event)
    return response


def reserve_main(event):
    try:
        table_name = common_env_vars.get_table_name(os.environ)

        identity = common_event.get_identity(event, os.environ)
        list_id = common_event.get_list_id(event)
        product_id = common_event.get_product_id(event)
        request_reserve_quantity = common_event.get_quantity(event)
        message = common_event.get_message(event)

        users_name = get_users_name(table_name, identity)
        product_quantities = get_product_quantities(table_name, list_id, product_id)
        new_product_reserved_quantity = update_reserved_quantities(product_quantities, request_reserve_quantity)

        add_reserved_details(table_name, list_id, product_id, identity, users_name, request_reserve_quantity, message)
        update_product_reserved_quantity(table_name, list_id, product_id, new_product_reserved_quantity)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'reserved': True}
    response = common.create_response(200, json.dumps(data))
    return response


def update_product_reserved_quantity(table_name, list_id, product_id, new_product_reserved_quantity):
    key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression="set reserved = :r",
            ExpressionAttributeValues={
                ':r': {'N': str(new_product_reserved_quantity)},
            },
            ReturnValues="UPDATED_NEW"
        )
        logger.info("Attributes updated: " + json.dumps(response['Attributes']))
    except Exception as e:
        logger.info("update item exception: " + str(e))
        raise Exception("Unexpected error when updating the list item.")

    return True


def add_reserved_details(table_name, list_id, product_id, user_id, users_name, quantity, message):
    item = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "RESERVED#PRODUCT#{}".format(product_id)},
        'name': {'S': users_name},
        'userId': {'S': user_id},
        'quantity': {'N': str(quantity)},
        'message': {'S': message},
        'reservedAt': {'N': str(int(time.time()))}
    }

    try:
        logger.info("Put reserved item for lists table: {}".format(item))
        dynamodb.put_item(TableName=table_name, Item=item)
    except Exception as e:
        logger.error("Reserved details item could not be added: {}".format(e))
        raise Exception('Reserved details item could not be added.')

    return True


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

    return response['Item']['name']['S']


def get_product_quantities(table_name, list_id, product_id):
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
        logger.info("No product id {} was found.".format(product_id))
        raise Exception("No product exists with this ID.")

    quantities = {
        'quantity': int(response['Item']['quantity']['N']),
        'reserved': int(response['Item']['reserved']['N'])
    }

    logger.info("Required quantity: {}, Reserved quantity: {}".format(quantities['quantity'], quantities['reserved']))

    return quantities


def update_reserved_quantities(quantities, reserved_quantity):
    logger.info("Updating reserved quantiy ({}) by reserved amount ({})".format(quantities['reserved'], reserved_quantity))
    new_reserved_quantity = quantities['reserved'] + reserved_quantity

    if new_reserved_quantity > quantities['quantity']:
        raise Exception("Reserved product quantity {} exceeds quantity required {}.".format(new_reserved_quantity, quantities['quantity']))

    return new_reserved_quantity
