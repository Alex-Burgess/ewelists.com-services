import json
import os
import boto3
import logging
from lists import common, common_table_ops
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = add_product_main(event)
    return response


def add_product_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common.get_identity(event, os.environ)
        list_id = common.get_path_parameter(event, 'id')
        product_id = common.get_path_parameter(event, 'productid')
        quantity = common.get_body_attribute(event, 'quantity')
        type = common.get_product_type(event)

        list_item = common_table_ops.get_list(table_name, identity, list_id)
        common.confirm_owner(identity, list_id, [list_item])

        message = create_product_item(table_name, list_id, product_id, type, quantity)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'message': message}
    response = common.create_response(200, json.dumps(data))
    return response


def create_product_item(table_name, list_id, product_id, type, quantity):
    item = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)},
        'type': {'S': type},
        'quantity': {'N': str(quantity)},
        'reserved': {'N': str(0)}
    }

    try:
        logger.info("Put product item: {}".format(item))
        response = dynamodb.put_item(
            TableName=table_name,
            Item=item,
            ConditionExpression='attribute_not_exists(PK)'
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            logger.info("Product {} already exists in list {}.".format(product_id, list_id))
            raise Exception("Product already exists in list.")
        else:
            logger.error("Product could not be created: {}".format(e))
            raise Exception('Product could not be created.')

    logger.info("Add response: {}".format(response))

    return True
