import json
import os
import boto3
from lists import common, common_table_ops, logger

log = logger.setup_logger()


def handler(event, context):
    log.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    log.info("Body attributes: {}".format(json.dumps(event['body'])))
    response = update_reserve_main(event)
    return response


def update_reserve_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        email_index = common.get_env_variable(os.environ, 'EMAIL_INDEX')
        resv_id_index = common.get_env_variable(os.environ, 'RESERVATIONID_INDEX')
        resv_id = common.get_path_parameter(event, 'id')
        request_reserve_quantity = common.get_body_attribute(event, 'quantity')

        user = common.get_user(event, os.environ, table_name, email_index)

        # Step 1 - get reserved item and product item.
        reservation_item = common_table_ops.get_reservation(table_name, resv_id_index, resv_id)
        common.confirm_reservation_owner(reservation_item, user['id'])
        common.gift_is_reserved(reservation_item)

        # Step 2 - Determine change to users reserved product quantity
        # (i.e. difference between requested quantity of user and current quantity reserved by user)
        product_item = common_table_ops.get_product_item(table_name, reservation_item['listId'], reservation_item['productId'])
        quantity_change = calculate_difference_to_reserved_item_quantity(reservation_item, request_reserve_quantity)

        # Step 3 - Calculate new reserved quantity of product
        new_product_reserved_quantity = common.calculate_new_reserved_quantity(product_item, quantity_change)

        # Step 4 - Update reserved details item and update product reserved quantities
        product_key = common.create_product_key(reservation_item['listId'], reservation_item['productId'])
        reservation_key = common.create_reservation_key(reservation_item)
        update_product_and_reservation(table_name, product_key, reservation_key, new_product_reserved_quantity, request_reserve_quantity)

    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    data = {'updated': True}
    response = common.create_response(200, json.dumps(data))
    return response


def calculate_difference_to_reserved_item_quantity(reserved_item, new_quantity):
    difference = new_quantity - reserved_item['quantity']

    if new_quantity <= 0:
        message = "Reserved quantity cannot be reduced to 0."
        log.info(message)
        raise Exception(message)

    if difference == 0:
        message = "There was no difference in update request to reserved item."
        log.info(message)
        raise Exception(message)

    return difference


def update_product_and_reservation(table_name, product_key, reservation_key, new_product_reserved_quantity, request_reserve_quantity):
    dynamodb = boto3.client('dynamodb')

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
                    'Update': {
                        'TableName': table_name,
                        'Key': reservation_key,
                        'UpdateExpression': "set quantity = :q",
                        'ExpressionAttributeValues': {
                            ':q': {'N': str(request_reserve_quantity)},
                        }
                    }
                }
            ]
        )

        log.info("Attributes updated: " + json.dumps(response))
    except Exception as e:
        log.info("Transaction write exception: " + str(e))
        raise Exception("Unexpected error when unreserving product.")

    return True
