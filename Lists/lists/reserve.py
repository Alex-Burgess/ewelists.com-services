import json
import os
import boto3
import logging
import time
from lists import common
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = update_product_main(event)
    return response


def update_product_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        list_id = common.get_list_id(event)
        product_id = common.get_product_id(event)
        request_reserve_q = common.get_quantity(event)
        message = 'A test message'
        users_name = get_users_name(table_name, identity['userPoolSub'])
        current_qs = get_product_quantities(table_name, list_id, product_id)
        new_reserved_total = update_reserved_quantities(current_qs, request_reserve_q)

        add_reserved_details(table_name,
                             list_id,
                             product_id,
                             identity['userPoolSub'],
                             users_name,
                             request_reserve_q,
                             current_qs['reserved'],
                             new_reserved_total,
                             message
                             )
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'reserved': True}
    response = common.create_response(200, json.dumps(data))
    return response


def add_reserved_details(table_name, list_id, product_id, user_id, users_name, request_reserve, current_reserved, total_reserved, message):
    key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    details_obj = {
        'name': {'S': users_name},
        'userId': {'S': user_id},
        'reserved': {'N': str(request_reserve)},
        'message': {'S': message},
        'reservedAt': {'N': str(int(time.time()))}
    }

    if (current_reserved > 0):
        update_expression = "set reservedDetails = list_append(reservedDetails, :r), reserved = :q"
    else:
        update_expression = "set reservedDetails = :r, reserved = :q"

    try:
        logger.info("Updating product with reserved quantity ({}) and reserved data {}".format(total_reserved, details_obj))
        response = dynamodb.update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression=update_expression,
            ExpressionAttributeValues={
                ':q': {'N': str(total_reserved)},
                ':r': {'L': [
                        {'M': details_obj}
                    ]}
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        logger.error("Product could not be updated. Error code: {}. Error message: {}".format(e.response['Error']['Code'], e.response['Error']['Message']))
        raise Exception('Unexpected error when updating product.')

    logger.info("Reserve response: {}".format(response))

    return True


def get_users_name(table_name, user_id):
    key = {
        'PK': {'S': "USER#" + user_id},
        'SK': {'S': "USER#" + user_id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        logger.info("Get user item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    if 'Item' not in response:
        logger.info("No user id {} was found.".format(user_id))
        raise Exception("No user exists with this ID.")

    return response['Item']['name']['S']


def get_product_quantities(table_name, list_id, product_id):
    key = {
        'PK': {'S': "LIST#" + list_id},
        'SK': {'S': "PRODUCT#" + product_id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
        logger.info("Get product item response: {}".format(response))
    except ClientError as e:
        print(e.response['Error']['Message'])

    if 'Item' not in response:
        logger.info("No product id {} was found.".format(product_id))
        raise Exception("No product exists with this ID.")

    quantities = {
        'quantity': int(response['Item']['quantity']['N']),
        'reserved': int(response['Item']['reserved']['N'])
    }

    logger.info("Required quantity: {}, Reserved quantity: {}".format(quantities['quantity'], quantities['reserved']))

    return quantities


def update_reserved_quantities(quantities, reserved_quantity):
    logger.info("Updating reserved quantiy ({}) by reserved amount ({})".format(quantities['reserved'], reserved_quantity))
    new_reserved_quantity = quantities['reserved'] + reserved_quantity

    if new_reserved_quantity > quantities['quantity']:
        raise Exception("Reserved product quantity {} exceeds quantity required {}.".format(new_reserved_quantity, quantities['quantity']))

    return new_reserved_quantity
