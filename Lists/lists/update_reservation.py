import json
import os
import boto3
import logging
from lists import common
from lists import common_env_vars
from lists import common_event

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
        table_name = common_env_vars.get_table_name(os.environ)
        identity = common_event.get_identity(event, os.environ)
        list_id = common_event.get_list_id(event)
        product_id = common_event.get_product_id(event)
        request_reserve_quantity = common_event.get_quantity(event)

        # get reserved data object
        reserved_details_item = get_reserved_details_item(table_name, list_id, product_id)

        # check user reserved item
        # confirm_user_reserved_product()

        # product_quantities = get_product_quantities(table_name, list_id, product_id)
        # new_product_reserved_quantity = update_reserved_quantities(product_quantities, request_reserve_quantity)
        # update_product_reserved_attribute(table_name, list_id, product_id, new_product_reserved_quantity)

        # Check quantity is > 0

        # update_reserved_quantity_attribute(table_name, list_id, product_id, identity, new_reserve_quantity)

    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'reserved': 'true'}
    response = common.create_response(200, json.dumps(data))
    return response


def get_reserved_details_item(table_name, list_id, product_id):

    return
