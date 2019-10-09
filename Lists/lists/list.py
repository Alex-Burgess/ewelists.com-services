import json
import os
import boto3
import logging
from lists import common

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = list_main(event)
    return response


def list_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        usersLists = get_lists(table_name, identity['cognitoIdentityId'])
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(usersLists))
    return response


def get_lists(table_name, cognito_identity_id):
    lists = {"lists": []}
    # list ID, title, description

    logger.info("Querying table")

    response = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression="userId = :userId",
        ExpressionAttributeValues={":userId":  {'S': cognito_identity_id}}
    )

    logger.info("Parsing response")

    for i in response['Items']:
        list = {}
        list['listId'] = i['listId']['S']
        list['title'] = i['title']['S']
        list['description'] = i['description']['S']
        list['occasion'] = i['occasion']['S']
        lists['lists'].append(list)

    return lists
