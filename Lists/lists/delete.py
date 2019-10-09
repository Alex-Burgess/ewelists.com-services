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
    response = delete_main(event)
    return response


def delete_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        list_id = common.get_list_id(event)
        message = delete_item(table_name, identity['cognitoIdentityId'], list_id)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'deleted': True, 'listId': list_id, 'message': message}

    response = common.create_response(200, json.dumps(data))
    return response


def delete_item(table_name, cognito_identity_id, list_id):
    logger.info("Deleting List ID: {} for user: {}.".format(list_id, cognito_identity_id))

    key = {
        'userId': {'S': cognito_identity_id},
        'listId': {'S': list_id}
    }

    try:
        response = dynamodb.delete_item(
            TableName=table_name,
            Key=key,
            ConditionExpression="listId = :list_id",
            ExpressionAttributeValues={":list_id":  {'S': list_id}}
        )
        logger.info("Delete response: {}".format(response))
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            logger.info("Delete request failed for List ID: {} and user {} as condition check for List ID failed.  List does not exist.".format(list_id, cognito_identity_id))
            raise Exception("List does not exist.")
        else:
            raise

    logger.info("Delete request successfull for List ID: {} and user: {}.".format(list_id, cognito_identity_id))
    message = "Delete request successfull for List ID: {} and user: {}.".format(list_id, cognito_identity_id)
    return message
