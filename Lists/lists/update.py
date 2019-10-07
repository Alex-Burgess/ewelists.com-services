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
    logger.info("Event: " + json.dumps(event))
    response = update_list_main(event)
    return response


def update_list_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        list_id = common.get_list_id(event)
        attribute_details = get_attribute_details(event)
        udatedNewAttributes = update_list(table_name, identity['cognitoIdentityId'], list_id, attribute_details)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = create_response(200, udatedNewAttributes)
    return response


def get_attribute_details(event):
    try:
        body = event['body']
        logger.info("Event body: " + json.dumps(body))
    except Exception:
        logger.error("API Event was empty.")
        raise Exception('API Event was empty.')

    try:
        attribute_details = json.loads(body)
    except Exception:
        logger.error("API Event did not contain a valid body.")
        raise Exception('API Event did not contain a valid body.')

    return attribute_details


def update_list(table_name, cognito_identity_id, list_id, attribute_details):
    logger.info("Querying table")

    key = {
        'userId': {'S': cognito_identity_id},
        'listId': {'S': list_id}
    }

    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression="set " + attribute_details["attribute_name"] + " = :a",
            ExpressionAttributeValues={
                ':a': {'S': attribute_details["attribute_value"]},
            },
            ReturnValues="UPDATED_NEW"
        )

    except ClientError as e:
        logger.info("update item response: " + json.dumps(e.response))
        raise Exception("Unexpected error when updating the list item")

    logger.info("update item response: " + json.dumps(response))

    return response['Attributes']


def create_response(code, body):
    logger.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response
