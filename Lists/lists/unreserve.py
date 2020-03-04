import json
import os
from lists import common, common_table_ops, logger

log = logger.setup_logger()


def handler(event, context):
    log.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    log.info("Body attributes: {}".format(json.dumps(event['body'])))
    response = unreserve_main(event)
    return response


def unreserve_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        index_name = common.get_env_variable(os.environ, 'INDEX_NAME')
        list_id = common.get_path_parameter(event, 'id')
        product_id = common.get_path_parameter(event, 'productid')

        # Step 1 - get identity (which could be from sign in, or email in path, or encrypted parameter)
        id = common.get_user(event, os.environ, table_name, index_name)['id']

        # Step 2 - get reserved item and product item.
        reserved_item = common_table_ops.get_reserved_details_item(table_name, list_id, product_id, id)
        product_item = common_table_ops.get_product_item(table_name, list_id, product_id)

        # Step 3 - Calculate new reserved quantity of product.
        new_product_reserved_quantity = common.calculate_new_reserved_quantity(product_item, -reserved_item['quantity'])

        # Step 4 - Delete reserved details item and update product reserved quantities
        common_table_ops.unreserve_product(table_name, list_id, product_id, reserved_item['reservationId'], id, new_product_reserved_quantity)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    data = {'unreserved': True}

    response = common.create_response(200, json.dumps(data))
    return response
