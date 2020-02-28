import json
import os
import boto3
import logging
from lists import common
from lists import common_table_ops
from lists import common_event

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = delete_product_main(event)
    return response


def delete_product_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common_event.get_identity(event, os.environ)
        list_id = common_event.get_list_id(event)
        product_id = common_event.get_product_id(event)

        list_item = common_table_ops.get_list(table_name, identity, list_id)
        common.confirm_owner(identity, list_id, [list_item])

        message = delete_product_item(table_name, list_id, product_id)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'message': message}
    response = common.create_response(200, json.dumps(data))
    return response


def delete_product_item(table_name, list_id, product_id):
    key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    condition = {
        ':PK': {'S': "LIST#{}".format(list_id)},
        ':SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    try:
        logger.info("Deleting product item: {}".format(key))
        response = dynamodb.delete_item(
            TableName=table_name,
            Key=key,
            ConditionExpression="PK = :PK AND SK = :SK",
            ExpressionAttributeValues=condition
        )
    except Exception as e:
        logger.error("Product could not be deleted: {}".format(e))
        raise Exception('Product could not be deleted.')

    logger.info("Delete response: {}".format(response))

    return True
