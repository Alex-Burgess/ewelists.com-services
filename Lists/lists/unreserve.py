import json
import os
import boto3
import logging
from lists import common
from lists import common_product
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    logger.info("Update product event: " + json.dumps(event))
    response = update_product_main(event)
    return response


def update_product_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        list_id = common.get_list_id(event)
        product_id = common.get_product_id(event)
        quantity = common.get_quantity(event)

        # list_item = common_product.get_list(table_name, identity['userPoolSub'], list_id)
        # common.confirm_owner(identity['userPoolSub'], list_id, [list_item])
        #
        # quantity = update_product_item(table_name, list_id, product_id, quantity)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'reserved': 'true'}
    response = common.create_response(200, json.dumps(data))
    return response
