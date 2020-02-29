import json
import os
import boto3
from lists import common, logger
from lists.common_entities import User, List

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = list_main(event)
    return response


def list_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        index_name = common.get_env_variable(os.environ, 'INDEX_NAME')
        identity = common.get_identity(event, os.environ)
        usersLists = get_lists(table_name, index_name, identity)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(usersLists))
    return response


def get_lists(table_name, index_name, cognito_user_id):
    response_data = {"user": None, "owned": []}

    log.info("Querying table")

    try:
        response = dynamodb.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression="userId = :userId",
            ExpressionAttributeValues={":userId":  {'S': cognito_user_id}}
        )
        log.info("All items in query response. ({})".format(response['Items']))
    except Exception as e:
        log.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting lists from table.")

    if len(response['Items']) > 0:
        for item in response['Items']:
            log.info("Checking response item: {}".format(item))
            if item['PK']['S'] == item['SK']['S']:
                log.info("Adding user item to response data. ({})".format(item))
                user = User(item)
                response_data['user'] = user.get_basic_details()
            elif item['SK']['S'] == 'USER#' + cognito_user_id:
                if item['listOwner']['S'] == cognito_user_id:
                    log.info("Adding owner list item to response data. ({})".format(item))
                    list_details = List(item).get_details()
                    response_data['owned'].append(list_details)

    else:
        log.info("0 lists were returned.")

    return response_data
