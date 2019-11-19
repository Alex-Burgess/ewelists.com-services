import json
import os
import boto3
import logging
from lists import common
from lists import common_env_vars
from lists import common_event
from lists import common_table_ops

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
        table_name = common_env_vars.get_table_name(os.environ)
        identity = common_event.get_identity(event, os.environ)
        list_id = common_event.get_list_id(event)
        product_id = common_event.get_product_id(event)

        # Step 1 - get reserved item and product item.
        reserved_item = common_table_ops.get_reserved_details_item(table_name, list_id, product_id, identity)
        product_item = common_table_ops.get_product_item(table_name, list_id, product_id)

        # Step 2 - Calculate new reserved quantity of product.
        new_product_reserved_quantity = common.calculate_new_reserved_quantity(product_item, -reserved_item['quantity'])

        # Step 3 - Delete reserved details item and update product reserved quantities
        update_product_and_delete_reserved_item(table_name, list_id, product_id, identity, new_product_reserved_quantity)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'unreserved': 'true'}

    response = common.create_response(200, json.dumps(data))
    return response


def update_product_and_delete_reserved_item(table_name, list_id, product_id, user_id, new_product_reserved_quantity):
    product_key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    reserved_key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "RESERVED#{}#{}".format(product_id, user_id)}
    }

    condition = {
        ':PK': {'S': "LIST#{}".format(list_id)},
        ':SK': {'S': "RESERVED#{}#{}".format(product_id, user_id)}
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
