import json
import os
import time
import uuid
import boto3
from botocore.exceptions import ClientError
from lists import common, common_table_ops, logger

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')

ses = boto3.client('ses', region_name='eu-west-1')
SENDER = "Ewelists <contact@ewelists.com>"


def handler(event, context):
    response = reserve_main(event)
    return response


def reserve_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')


    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    data = {'purchased': True}
    response = common.create_response(200, json.dumps(data))
    return response
