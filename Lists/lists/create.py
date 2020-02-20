import json
import os
import boto3
import logging
import time
import uuid
from lists import common
from lists import common_env_vars
from lists import common_event
from lists import common_table_ops

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
        table_name = common_env_vars.get_table_name(os.environ)
        identity = common_event.get_identity(event, os.environ)
        users_name = common_table_ops.get_users_details(table_name, identity)['name']
        listId = generate_list_id()
        attributes = get_attribute_details(event)
        message = put_item_in_table(table_name, identity, listId, attributes, users_name)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'listId': listId, 'message': message}

    response = common.create_response(200, json.dumps(data))
    return response


def put_item_in_table(table_name, cognito_user_id, listId, attributes, users_name):
    item = {
        'PK': {'S': "LIST#{}".format(listId)},
        'SK': {'S': "USER#{}".format(cognito_user_id)},
        'listId': {'S': listId},
        "listOwner": {'S': cognito_user_id},
        'userId': {'S': cognito_user_id},
        'title': {'S': attributes['title']},
        'occasion': {'S': attributes['occasion']},
        'description': {'S': attributes['description']},
        'createdAt': {'N': str(int(time.time()))},
        'imageUrl': {'S': attributes['imageUrl']},
    }

    if 'eventDate' in attributes:
        item['eventDate'] = {'S': attributes['eventDate']}

    try:
        logger.info("Put owned item for lists table: {}".format(item))
        dynamodb.put_item(TableName=table_name, Item=item)
    except Exception as e:
        logger.error("List could not be created: {}".format(e))
        raise Exception('List could not be created.')

    try:
        item['SK']['S'] = "SHARED#{}".format(cognito_user_id)
        item['shared_user_name'] = {'S': users_name}
        logger.info("Put shared item for lists table: {}".format(item))
        dynamodb.put_item(TableName=table_name, Item=item)
    except Exception as e:
        logger.error("List shared item for owner could not be created: {}".format(e))
        raise Exception('List shared item for owner could not be created.')

    message = "List was created."

    return message


def generate_list_id():
    # Generate a random uid
    newlistId = str(uuid.uuid4())
    logger.info("Generated List ID: {}".format(newlistId))

    return newlistId


def get_attribute_details(event):
    if event['body'] == "null":
        raise Exception('API Event Body was empty.')

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
