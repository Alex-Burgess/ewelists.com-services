import json
import os
import logging
from lists import common, common_table_ops

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


def handler(event, context):
    logger.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    logger.info("Body attributes: {}".format(json.dumps(event['body'])))
    response = unreserve_main(event)
    return response


def unreserve_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        list_id = common.get_path_parameter(event, 'id')
        product_id = common.get_path_parameter(event, 'productid')

        # Step 1 - get identity (which could be from sign in, or email in path, or encrypted parameter)
        id = common.get_user(event, os.environ, table_name)['id']

        # Step 2 - get reserved item and product item.
        reserved_item = common_table_ops.get_reserved_details_item(table_name, list_id, product_id, id)
        product_item = common_table_ops.get_product_item(table_name, list_id, product_id)

        # Step 3 - Calculate new reserved quantity of product.
        new_product_reserved_quantity = common.calculate_new_reserved_quantity(product_item, -reserved_item['quantity'])

        # Step 4 - Delete reserved details item and update product reserved quantities
        common_table_ops.unreserve_product(table_name, list_id, product_id, id, new_product_reserved_quantity)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'unreserved': True}

    response = common.create_response(200, json.dumps(data))
    return response
