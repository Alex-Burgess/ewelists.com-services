import json
import os
import boto3
import logging
from products import common
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = delete_main(event)
    return response


def delete_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        product_id = common.get_product_id(event)
        delete_product(table_name, product_id)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'deleted': True}
    response = common.create_response(200, json.dumps(data))
    return response


def delete_product(table_name, product_id):
    logger.info("Deleting Product ID: {}.".format(product_id))

    key = {
        'productId': {'S': product_id},
    }

    try:
        response = dynamodb.delete_item(
            TableName=table_name,
            Key=key,
        )
        logger.info("Delete response: {}".format(response))
    except ClientError as e:
        logger.error("Delete failed exception: " + e)
        raise Exception("Product can not be deleted.")

    return True
