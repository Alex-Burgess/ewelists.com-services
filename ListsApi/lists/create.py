import json
import os
import boto3
import logging
import time

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
    item = {
        'userId': {'S': '12345678'},
        'listId': {'S': '1234abcd'},
        'createdAt': {'N': str(int(time.time()))}
    }

    try:
        table_name = get_table_name()
        dynamodb.put_item(TableName=table_name, Item=item)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    body = "List was created with ID: 1234abcd"
    response = create_response(200, body)
    return response


def get_table_name():
    try:
        table_name = os.environ['TABLE_NAME']
        logger.info("TABLE_NAME environment variable value: " + table_name)
    except KeyError:
        logger.error('TABLE_NAME environment variable not set correctly')
        raise Exception('TABLE_NAME environment variable not set correctly')

    return table_name


def create_response(code, body):
    logger.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response
