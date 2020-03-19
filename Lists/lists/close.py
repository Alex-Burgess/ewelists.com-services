import json
import os
import boto3
from lists import common, logger

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    log.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    response = close_main(event)
    return response


def close_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common.get_identity(event, os.environ)
        list_id = common.get_path_parameter(event, 'id')
        common.confirm_owner(table_name, identity, list_id)

        update_list(table_name, identity, list_id)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    data = {'closed': True, 'listId': list_id}

    response = common.create_response(200, json.dumps(data))
    return response


def update_list(table_name, user_id, list_id):
    key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "USER#{}".format(user_id)}
    }

    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression="set #st = :s",
            ExpressionAttributeValues={
                ':s': {'S': 'closed'},
            },
            ExpressionAttributeNames={
                '#st': 'state'
            },
            ReturnValues="UPDATED_NEW"
        )

    except Exception as e:
        log.info("update item exception: " + str(e))
        raise Exception("Unexpected error when updating the list item.")

    log.info("Attributes updated: " + json.dumps(response['Attributes']))

    return True
