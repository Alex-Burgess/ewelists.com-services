import json
import os
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


def handler(event, context):
    response = unreserve_main(event)
    return response


def unreserve_main(event):
    try:
        table_name = common_env_vars.get_table_name(os.environ)
        list_id = common_event.get_list_id(event)
        product_id = common_event.get_product_id(event)

        # Step 1 - get identity (which could be from sign in, or email in path, or encrypted parameter)
        identity = common_event.get_identity(event, os.environ)
        # TODO - add in checks for email on path.

        # Step 2 - get reserved item and product item.
        reserved_item = common_table_ops.get_reserved_details_item(table_name, list_id, product_id, identity)
        product_item = common_table_ops.get_product_item(table_name, list_id, product_id)

        # Step 3 - Calculate new reserved quantity of product.
        new_product_reserved_quantity = common.calculate_new_reserved_quantity(product_item, -reserved_item['quantity'])

        # Step 4 - Delete reserved details item and update product reserved quantities
        common_table_ops.unreserve_product(table_name, list_id, product_id, identity, new_product_reserved_quantity)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'unreserved': True}

    response = common.create_response(200, json.dumps(data))
    return response
