import json
import os
import boto3
from lists import common, common_table_ops, logger

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    log.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    log.info("Body attributes: {}".format(json.dumps(event['body'])))
    response = unreserve_main(event)
    return response


def unreserve_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        email_index = common.get_env_variable(os.environ, 'EMAIL_INDEX')
        resv_id_index = common.get_env_variable(os.environ, 'RESERVATIONID_INDEX')
        resv_id = common.get_path_parameter(event, 'id')

        # Step 1 - get identity (which could be from sign in, or email in path, or encrypted parameter)
        user = common.get_user(event, os.environ, table_name, email_index)

        # Step 2 - get reserved item. Check reserved item is in reserved state, i.e. not purchased or cancelled.
        reservation = common_table_ops.get_reservation(table_name, resv_id_index, resv_id)
        common.confirm_reservation_owner(reservation, user['id'])
        common.gift_is_reserved(reservation)

        # Step 3 - Get product Item. Calculate new reserved quantity of product.
        product_item = common_table_ops.get_product_item(table_name, reservation['listId'], reservation['productId'])
        new_product_reserved_quantity = common.calculate_new_reserved_quantity(product_item, -reservation['quantity'])

        # Step 4 - Delete reserved details item and update product reserved quantities
        product_key = common.create_product_key(reservation['listId'], reservation['productId'])
        reservation_key = common.create_reservation_key(reservation)
        unreserve_product(table_name, product_key, reservation_key, new_product_reserved_quantity)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    data = {'unreserved': True}

    response = common.create_response(200, json.dumps(data))
    return response


def unreserve_product(table_name, product_key, reservation_key, new_product_reserved_quantity):
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
                        'UpdateExpression': "set #st = :s",
                        'ExpressionAttributeValues': {
                            ':s': {'S': 'cancelled'},
                        },
                        'ExpressionAttributeNames': {
                            '#st': 'state'
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
