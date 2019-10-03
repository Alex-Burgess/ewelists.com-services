import json
import os
import boto3
import logging
import time
import uuid

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
    try:
        table_name = get_table_name()
        cognitoIdentityId = getIdentity(event, 'cognitoIdentityId')
        userPoolSub = getIdentity(event, 'cognitoAuthenticationProvider')
        listId = generate_listId(cognitoIdentityId, table_name)
        message = put_item_in_table(table_name, cognitoIdentityId, userPoolSub, listId)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = create_response(200, message)
    return response


def generate_listId(cognitoIdentityId, table_name):
    # Generate a random uid, then check that the user does not already have a list with that ID.
    Invalid = True
    while Invalid:
        newlistId = uuid.uuid4().hex[:8]
        logger.info("Generated List ID: {}".format(newlistId))

        key = {
            'userId': {'S': cognitoIdentityId},
            'listId': {'S': newlistId}
        }

        response = dynamodb.get_item(TableName=table_name, Key=key)

        if 'Item' in response:
            logger.info("Generated List ID existed: {}".format(response))
        else:
            logger.info("List ID ({}) unique in table for user: {}".format(newlistId, cognitoIdentityId))
            Invalid = False

    return newlistId


def put_item_in_table(table_name, cognitoIdentityId, userPoolSub, listId):
    item = {
        'userId': {'S': cognitoIdentityId},
        'userPoolSub': {'S': userPoolSub},
        'listId': {'S': listId},
        'createdAt': {'N': str(int(time.time()))}
    }

    logger.info("Put item for lists table: {}".format(item))

    try:
        dynamodb.put_item(TableName=table_name, Item=item)
    except Exception as e:
        logger.error("List not could be created: {}".format(e))
        raise

    message = "List was created with ID: " + listId

    return message


def getIdentity(event, name):
    try:
        id = event['requestContext']['identity'][name]
    except KeyError:
        logger.error("There was no {} in the API event.".format(name))
        raise Exception("There was no {} in the API event.".format(name))

    if id is None:
        logger.info("API Event contained {}: {}".format(name, id))
        raise Exception("There was no {} in the API event.".format(name))

    if name == 'cognitoAuthenticationProvider':
        id = id.split(':')[-1]

    return id


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
