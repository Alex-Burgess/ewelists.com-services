import json
import os
import time
import uuid
import boto3
import logging
from lists import common
from lists import common_env_vars
from lists import common_event
from lists import common_table_ops

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    logger.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    response = reservation_main(event)
    return response


def reservation_main(event):
    try:
        table_name = common_env_vars.get_table_name(os.environ)
        resv_id = common_event.get_path_parameter(event, 'id')

    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {
        'user_id': '123456789',
        'user_email': 'test.user@gmail.com',
        'user_name': 'Test User',
        'list_id': '3205c3b8-4b0d-4e99-b097-c1deb559788e',
        'list_title': 'This is a List',
        'product_id': '12345678-blog-e002-1234-abcdefghijkl',
        'product_type': 'products',
        'quantity': 1,
        'state': 'reserved',
    }
    response = common.create_response(200, json.dumps(data))
    return response
