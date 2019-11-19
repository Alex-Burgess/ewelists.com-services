import json
import os
import boto3
import logging
from lists import common
from lists import common_table_ops
from lists import common_env_vars
from lists import common_event
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
        table_name = common_env_vars.get_table_name(os.environ)
        identity = common_event.get_identity(event, os.environ)
        list_id = common_event.get_list_id(event)
        product_id = common_event.get_product_id(event)
        quantity = common_event.get_quantity(event)

        list_item = common_table_ops.get_list(table_name, identity, list_id)
        common.confirm_owner(identity, list_id, [list_item])

        quantity = update_product_item(table_name, list_id, product_id, quantity)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'quantity': quantity}
    response = common.create_response(200, json.dumps(data))
    return response


def update_product_item(table_name, list_id, product_id, quantity):
    key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    try:
        logger.info("Updating quantity of product item ({}) to {}".format(key, quantity))
        response = dynamodb.update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression="set quantity = :q",
            ExpressionAttributeValues={
                ':q': {'N': str(quantity)},
            },
            ConditionExpression="attribute_exists(PK)",
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        logger.error("Exception: {}.".format(e))
        logger.error("Product could not be updated. Error code: {}. Error message: {}".format(e.response['Error']['Code'], e.response['Error']['Message']))

        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise Exception('Product did not exist.')
        else:
            raise Exception('Unexpected error when updating product.')

    logger.info("Add response: {}".format(response))

    if 'quantity' in response['Attributes']:
        quantity = int(response['Attributes']['quantity']['N'])
    else:
        raise Exception('No updates to quantity were required.')

    return quantity
