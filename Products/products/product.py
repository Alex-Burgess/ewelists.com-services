import json
import os
import boto3
import logging
from products import common

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    logger.info("event: " + json.dumps(event))
    response = search_main(event)
    return response


def search_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        # product_url = get_url(event)
        # product = url_query(table_name, index_name, product_url)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    # data = {'product': product}
    data = {'product': '12345678'}
    response = common.create_response(200, json.dumps(data))
    return response
