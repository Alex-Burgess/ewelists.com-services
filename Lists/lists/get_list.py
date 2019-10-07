import json
import os
import boto3
import logging
from lists import common
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = get_list_main(event)
    return response


def get_list_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        list_id = common.get_list_id(event)
        usersLists = get_list_query(table_name, identity['cognitoIdentityId'], list_id)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = create_response(200, json.dumps(usersLists))
    return response


def get_list_query(table_name, cognito_identity_id, list_id):
    logger.info("Querying table")

    key = {
        'userId': {'S': cognito_identity_id},
        'listId': {'S': list_id}
    }

    try:
        response = dynamodb.get_item(TableName=table_name, Key=key)
        # item = response['Item']
    except ClientError as e:
        logger.info("get item response" + json.dumps(e.response))
        raise Exception("Unexpected error when getting list item from table.")

    if 'Item' not in response:
        logger.info("List ID ({} did not exist in table for user: {})".format(list_id, cognito_identity_id))
        raise Exception("List does not exist.")

    item = response['Item']

    return item


def create_response(code, body):
    logger.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response
