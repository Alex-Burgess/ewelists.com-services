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
    response = reserve_main(event)
    return response


def reserve_main(event):
    try:
        table_name = common_env_vars.get_table_name(os.environ)
        index_name = common_env_vars.get_table_index(os.environ)
        template = common_env_vars.get_template_name(os.environ)
        list_id = common_event.get_list_id(event)
        product_id = common_event.get_product_id(event)
        request_reserve_quantity = common_event.get_quantity(event)

        # Step 1 - check if reserved item exists
        user = common.get_user(event, os.environ, table_name)
        common_table_ops.check_product_not_reserved_by_user(table_name, list_id, product_id, user['id'])

        if not user['exists']:
            if common_table_ops.does_user_have_account(table_name, index_name, user['email']):
                raise Exception("User has an account, login required before product can be reserved.")

        # Step 2 - get product item.
        product_item = common_table_ops.get_product_item(table_name, list_id, product_id)

        # Step 3 - Calculate new reserved quantity of product.
        new_product_reserved_quantity = common.calculate_new_reserved_quantity(product_item, request_reserve_quantity)

        # Step 4 - Update, in one transaction, the product reserved quantity and create reserved item.
        common_table_ops.create_reservation(table_name, list_id, product_id, new_product_reserved_quantity, request_reserve_quantity, user['id'], user['name'])

        # Step 5 - Send reserve confirmation email
        common.send_email(user['email'], user['name'], template)

    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'reserved': True}
    response = common.create_response(200, json.dumps(data))
    return response
