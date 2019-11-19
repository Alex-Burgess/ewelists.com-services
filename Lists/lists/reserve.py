import json
import os
import boto3
import logging
import time
from lists import common
from lists import common_env_vars
from lists import common_event
from lists import common_table_ops
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

        users_name = common_table_ops.get_users_name(table_name, identity)

        # Step 1 - get product item.
        product_item = common_table_ops.get_product_item(table_name, list_id, product_id)

        # Step 2 - check if reserved item exists
        check_no_reserved_details_item(table_name, list_id, product_id, identity)

        # Step 3 - Calculate new reserved quantity of product.
        new_product_reserved_quantity = common.calculate_new_reserved_quantity(product_item, request_reserve_quantity)

        # Step 4 - Update, in one transaction, the product reserved quantity and create reserved item.
        update_product_and_create_reserved_item(table_name, list_id, product_id, new_product_reserved_quantity, request_reserve_quantity, identity, users_name, message)

    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'reserved': True}
    response = common.create_response(200, json.dumps(data))
    return response


def update_product_and_create_reserved_item(table_name, list_id, product_id, new_product_reserved_quantity, request_reserve_quantity, user_id, users_name, message):
    product_key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    reserved_item = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "RESERVED#{}#{}".format(product_id, user_id)},
        'name': {'S': users_name},
        'productId': {'S': product_id},
        'userId': {'S': user_id},
        'quantity': {'N': str(request_reserve_quantity)},
        'message': {'S': message},
        'reservedAt': {'N': str(int(time.time()))}
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
                    'Put': {
                        'TableName': table_name,
                        'Item': reserved_item
                    }
                }
            ]
        )

        logger.info("Attributes updated: " + json.dumps(response))
    except Exception as e:
        logger.info("Transaction write exception: " + str(e))
        raise Exception("Unexpected error when unreserving product.")

    return True


def check_no_reserved_details_item(table_name, list_id, product_id, user_id):
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

    if 'Item' in response:
        logger.info("Reserved product was found for list {}, product id {} and user {}.".format(list_id, product_id, user_id))
        raise Exception("Product already reserved by user.")

    return True
