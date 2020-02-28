import json
import os
import boto3
import logging
from lists import common, common_table_ops

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = unshare_main(event)
    return response


def unshare_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common.get_identity(event, os.environ)
        list_id = common.get_path_parameter(event, 'id')
        list = common_table_ops.get_list(table_name, identity, list_id)
        common.confirm_owner(identity, list_id, [list])

        share_type = common.get_share_type(event)

        if share_type == "SHARED":
            user_id = common.get_path_parameter(event, 'user')
            delete_shared_item(table_name, list_id, user_id)
        elif share_type == "PENDING":
            email = common.get_path_parameter(event, 'user')
            delete_pending_item(table_name, list_id, email)
        else:
            raise Exception('Shared user had wrong type.')

    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'unshared': True}
    response = common.create_response(200, json.dumps(data))
    return response


def delete_shared_item(table_name, list_id, user_id):
    key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "SHARED#{}".format(user_id)}
    }

    condition = {
        ':PK': {'S': "LIST#{}".format(list_id)},
        ':SK': {'S': "SHARED#{}".format(user_id)}
    }

    try:
        logger.info("Deleting shared item: {}".format(key))
        response = dynamodb.delete_item(
            TableName=table_name,
            Key=key,
            ConditionExpression="PK = :PK AND SK = :SK",
            ExpressionAttributeValues=condition
        )
    except Exception as e:
        logger.error("Shared user could not be deleted: {}".format(e))
        raise Exception('Shared user could not be deleted.')

    logger.info("Delete response: {}".format(response))

    return True


def delete_pending_item(table_name, list_id, email):
    key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PENDING#{}".format(email)}
    }

    condition = {
        ':PK': {'S': "LIST#{}".format(list_id)},
        ':SK': {'S': "PENDING#{}".format(email)}
    }

    try:
        logger.info("Deleting pending item: {}".format(key))
        response = dynamodb.delete_item(
            TableName=table_name,
            Key=key,
            ConditionExpression="PK = :PK AND SK = :SK",
            ExpressionAttributeValues=condition
        )
    except Exception as e:
        logger.error("Pending shared user could not be deleted: {}".format(e))
        raise Exception('Pending shared user could not be deleted.')

    logger.info("Delete response: {}".format(response))

    return True
