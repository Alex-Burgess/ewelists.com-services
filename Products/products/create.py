import json
import os
import boto3
import logging
import time
import uuid
from products import common

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = create_main(event)
    return response


def create_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        product_info = get_product_info(event)
        product_id = put_product(table_name, product_info)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'productId': product_id, 'message': 'success'}
    response = common.create_response(200, json.dumps(data))
    return response


def get_product_info(event):
    if event['body'] == "null":
        raise Exception('API Event Body was empty.')

    try:
        body = event['body']
        logger.info("Event body: " + json.dumps(body))
    except Exception:
        logger.error("API Event was empty.")
        raise Exception('API Event was empty.')

    try:
        attribute_details = json.loads(body)
        logger.info("Attributes for create: " + json.dumps(attribute_details))
    except Exception:
        logger.error("API Event did not contain a valid body.")
        raise Exception('API Event did not contain a valid body.')

    return attribute_details


def put_product(table_name, product_info):
    product_id = str(uuid.uuid4())
    item = {
        'productId': {'S': product_id},
        'retailer': {'S': product_info['retailer']},
        'brand': {'S': product_info['brand']},
        'details': {'S': product_info['details']},
        'productUrl': {'S': product_info['productUrl']},
        'imageUrl': {'S': product_info['imageUrl']},
        'createdAt': {'N': str(int(time.time()))}
    }

    try:
        logger.info("Product item to be put in table: {}".format(item))
        dynamodb.put_item(TableName=table_name, Item=item)
    except Exception as e:
        logger.error("Product could not be created: {}".format(e))
        raise Exception('Product could not be created.')

    return product_id
