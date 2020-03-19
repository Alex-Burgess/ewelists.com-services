import json
import os
import boto3
import time
import uuid
from lists import common, common_table_ops, logger

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = create_main(event)
    return response


def create_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common.get_identity(event, os.environ)
        users_name = common_table_ops.get_users_details(table_name, identity)['name']
        listId = generate_list_id()
        attributes = get_attribute_details(event)
        put_item_in_table(table_name, identity, listId, attributes, users_name)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    data = {'listId': listId}

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
        'state': {'S': 'open'},
    }

    if 'eventDate' in attributes:
        item['eventDate'] = {'S': attributes['eventDate']}

    try:
        log.info("Put owned item for lists table: {}".format(item))
        dynamodb.put_item(TableName=table_name, Item=item)
    except Exception as e:
        log.error("List could not be created: {}".format(e))
        raise Exception('List could not be created.')

    return True


def generate_list_id():
    newlistId = str(uuid.uuid4())
    log.info("Generated List ID: {}".format(newlistId))

    return newlistId


def get_attribute_details(event):
    if event['body'] == "null":
        raise Exception('API Event Body was empty.')

    try:
        body = event['body']
        log.info("Event body: " + json.dumps(body))
    except Exception:
        raise Exception('API Event was empty.')

    try:
        attribute_details = json.loads(body)
        log.info("Attributes for create: " + json.dumps(attribute_details))
    except Exception:
        raise Exception('API Event did not contain a valid body.')

    return attribute_details
