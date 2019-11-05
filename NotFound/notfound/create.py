import json
import os
import boto3
import logging
import time
import uuid
from notfound import common

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    # response = create_main(event)
    logger.info("Incoming event: {}".format(event))

    data = {'productId': '12345678', 'message': 'success'}
    response = common.create_response(200, json.dumps(data))
    return response
