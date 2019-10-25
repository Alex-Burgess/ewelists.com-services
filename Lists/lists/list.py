import json
import os
import boto3
import logging
from lists import common
from lists.entities import User, List

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
        index_name = "userId-index"
        identity = common.get_identity(event, os.environ)
        # usersLists = get_lists(table_name, index_name, identity['cognitoIdentityId'])
        usersLists = get_lists(table_name, index_name, identity['userPoolSub'])
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(usersLists))
    return response


def get_lists(table_name, index_name, cognito_identity_id):
    response_data = {"user": None, "owned": [], "shared": []}

    logger.info("Querying table")

    try:
        response = dynamodb.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression="userId = :userId",
            ExpressionAttributeValues={":userId":  {'S': cognito_identity_id}}
        )
        logger.info("All items in query response. ({})".format(response['Items']))
    except Exception as e:
        logger.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting lists from table.")

    if len(response['Items']) > 0:
        for item in response['Items']:
            if item['PK']['S'] == item['SK']['S']:
                logger.info("Adding user item to response data. ({})".format(item))
                user = User(item)
                response_data['user'] = user.get_basic_details()
            elif item['listOwner']['S'] == cognito_identity_id and item['SK']['S'].startswith("USER"):
                logger.info("Adding owner list item to response data. ({})".format(item))
                list_details = List(item).get_details()
                response_data['owned'].append(list_details)
            elif item['listOwner']['S'] != cognito_identity_id and item['SK']['S'].startswith("SHARE"):
                logger.info("Adding list shared with user to response data. ({})".format(item))
                list_details = List(item).get_details()
                response_data['shared'].append(list_details)
    else:
        logger.info("0 lists were returned.")

    return response_data
