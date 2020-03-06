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
        index_name = common.get_env_variable(os.environ, 'INDEX_NAME')
        list_id = common.get_path_parameter(event, 'id')
        product_id = common.get_path_parameter(event, 'productid')

        # Step 1 - get identity (which could be from sign in, or email in path, or encrypted parameter)
        user = common.get_user(event, os.environ, table_name, index_name)

        # Step 2 - get reserved item and product item.  Check reserved item is in reserved state, i.e. not purchased or cancelled.
        reserved_item = common_table_ops.get_reserved_details_item(table_name, list_id, product_id, user['id'])
        product_item = common_table_ops.get_product_item(table_name, list_id, product_id)
        common.gift_is_reserved(reserved_item)

        # Step 3 - Calculate new reserved quantity of product.
        new_product_reserved_quantity = common.calculate_new_reserved_quantity(product_item, -reserved_item['quantity'])

        # Step 4 - Delete reserved details item and update product reserved quantities
        product_key = common.create_product_key(list_id, product_id)
        reserved_key = common.create_reserved_key(list_id, product_id, user)
        reservation_key = common.create_reservation_key(reserved_item['reservationId'])
        condition = create_condition(list_id, product_id, user['id'])
        unreserve_product(table_name, product_key, reserved_key, reservation_key, condition, new_product_reserved_quantity)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    data = {'unreserved': True}

    response = common.create_response(200, json.dumps(data))
    return response


def create_condition(list_id, product_id, user_id):
    return {
        ':PK': {'S': "LIST#{}".format(list_id)},
        ':SK': {'S': "RESERVED#{}#{}".format(product_id, user_id)}
    }


def unreserve_product(table_name, product_key, reserved_key, reservation_key, condition, new_product_reserved_quantity):
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
