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
        response_items = get_list_query(table_name, identity['userPoolSub'], list_id)
        common.confirm_owner(identity['userPoolSub'], list_id, response_items)
        list_object = common.generate_list_object(response_items)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(list_object))
    return response


def get_list_query(table_name, cognito_user_id, list_id):
    logger.info("Querying table {} for list ID {} owned by user ID {} .".format(table_name, cognito_user_id, list_id))

    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        logger.info("Response: " + json.dumps(response))
    except ClientError as e:
        logger.info("get item response: " + json.dumps(e.response))
        raise Exception("Unexpected error when getting list item from table.")

    if len(response['Items']) == 0:
        logger.info("No query results for List ID {} and user: {}.".format(list_id, cognito_user_id))
        raise Exception("No query results for List ID {} and user: {}.".format(list_id, cognito_user_id))

    return response['Items']
