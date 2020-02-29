import json
import os
import boto3
from lists import common, logger

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    log.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    response = reservation_main(event)
    return response


def reservation_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        resv_id = common.get_path_parameter(event, 'id')

    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
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
