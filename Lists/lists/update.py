import json
import os
import boto3
import logging
from lists import common

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = update_list_main(event)
    return response


def update_list_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        list_id = common.get_list_id(event)
        attribute_details = get_attribute_details(event)
        updated_attributes = update_list(table_name, identity['cognitoIdentityId'], list_id, attribute_details)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(updated_attributes))
    return response


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
        update_attributes = json.loads(body)
    except Exception:
        logger.error("API Event did not contain a valid body.")
        raise Exception('API Event did not contain a valid body.')

    expected_keys = ["title", "description", "occasion"]

    if list(update_attributes.keys()) != expected_keys:
        logger.error("Event body did not contain the expected keys " + str(expected_keys) + ".")
        raise Exception("Event body did not contain the expected keys " + str(expected_keys) + ".")

    return update_attributes


def update_list(table_name, cognito_identity_id, list_id, update_attributes):
    logger.info("Updating item in table with attribute values: " + json.dumps(update_attributes))

    key = {
        'userId': {'S': cognito_identity_id},
        'listId': {'S': list_id}
    }

    try:
        response = dynamodb.update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression="set title = :t, description = :d, occasion = :o",
            ExpressionAttributeValues={
                ':t': {'S': update_attributes["title"]},
                ':d': {'S': update_attributes["description"]},
                ':o': {'S': update_attributes["occasion"]}
            },
            ReturnValues="UPDATED_NEW"
        )

    except Exception as e:
        logger.info("update item exception: " + str(e))
        raise Exception("Unexpected error when updating the list item.")

    logger.info("update item response: " + json.dumps(response))

    return response['Attributes']
