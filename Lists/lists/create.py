import json
import os
import boto3
import logging
import time
import uuid
from lists import common

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
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        listId = generate_list_id(identity['cognitoIdentityId'], table_name)
        attributes = get_attribute_details(event)
        message = put_item_in_table(table_name, identity['cognitoIdentityId'], identity['userPoolSub'], listId, attributes)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'listId': listId, 'message': message}

    response = common.create_response(200, json.dumps(data))
    return response


def put_item_in_table(table_name, cognito_identity_id, user_pool_sub, listId, attributes):
    item = {
        'userId': {'S': cognito_identity_id},
        'userPoolSub': {'S': user_pool_sub},
        'listId': {'S': listId},
        'title': {'S': attributes['title']},
        'description': {'S': attributes['description']},
        'occasion': {'S': attributes['occasion']},
        'createdAt': {'N': str(int(time.time()))}
    }

    logger.info("Put item for lists table: {}".format(item))

    try:
        dynamodb.put_item(TableName=table_name, Item=item)
    except Exception as e:
        logger.error("List could not be created: {}".format(e))
        raise Exception('List could not be created.')

    message = "List was created."

    return message


def generate_list_id(cognito_identity_id, table_name):
    # Generate a random uid, then check that the user does not already have a list with that ID.
    Invalid = True
    while Invalid:
        newlistId = uuid.uuid4().hex[:8]
        logger.info("Generated List ID: {}".format(newlistId))

        key = {
            'userId': {'S': cognito_identity_id},
            'listId': {'S': newlistId}
        }

        response = dynamodb.get_item(TableName=table_name, Key=key)

        if 'Item' in response:
            logger.info("Generated List ID existed: {}".format(response))
        else:
            logger.info("List ID ({}) unique in table for user: {}".format(newlistId, cognito_identity_id))
            Invalid = False

    return newlistId


def get_attribute_details(event):
    try:
        body = event['body']
        logger.info("Event body: " + json.dumps(body))
    except Exception:
        logger.error("API Event was empty.")
        raise Exception('API Event was empty.')

    try:
        attribute_details = json.loads(body)
        logger.info("Attributes for create: " + json.dumps(attribute_details))
    except Exception:
        logger.error("API Event did not contain a valid body.")
        raise Exception('API Event did not contain a valid body.')

    return attribute_details
