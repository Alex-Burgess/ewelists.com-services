import json
import os
import boto3
import logging
from notfound import common
from notfound.entities import Product
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = get_main(event)
    return response


def get_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        product_id = common.get_product_id(event)
        product_object = get_product(table_name, product_id)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(product_object))
    return response


def get_product(table_name, product_id):
    key = {'productId': {'S': product_id}}

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
    except ClientError as e:
        logger.error("Exception: {}.".format(e))
        raise Exception("Unexpected problem getting product from table.")

    logger.info("Get product item response: {}".format(response))

    if 'Item' not in response:
        logger.info("No product returned for the id {}.".format(product_id))
        raise Exception("No product exists with this ID.")

    product = Product(response['Item'])

    return product.get_details()
