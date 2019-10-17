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

# TODO - should use batch write to delete items more efficiently.


def handler(event, context):
    response = delete_main(event)
    return response


def delete_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        list_id = common.get_list_id(event)
        items = get_items_associated_with_list(table_name, list_id)
        check_request_user_owns_list(identity['cognitoIdentityId'], items)
        message = delete_items(table_name, identity['cognitoIdentityId'], list_id, items)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'deleted': True, 'listId': list_id, 'message': message, "count": len(items)}

    response = common.create_response(200, json.dumps(data))
    return response


def delete_items(table_name, cognito_identity_id, list_id, items):
    logger.info("Deleting List ID: {} for user: {}.".format(list_id, cognito_identity_id))

    for item in items:
        logger.info("Deleting item with key: PK={}, SK={}".format(item['PK']['S'], item['SK']['S']))
        key = {
            'PK': {'S': item['PK']['S']},
            'SK': {'S': item['SK']['S']}
        }

        try:
            response = dynamodb.delete_item(
                TableName=table_name,
                Key=key,
                ConditionExpression="PK = :PK",
                ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
            )
            logger.info("Delete response: {}".format(response))
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                logger.info("Delete request failed for List ID: {} and user {} as condition check for List ID failed.  List does not exist.".format(list_id, cognito_identity_id))
                raise Exception("List does not exist.")
            else:
                raise

    logger.info("Deleted all items [{}] for List ID: {} and user: {}.".format(len(items), list_id, cognito_identity_id)),
    message = "Deleted all items [{}] for List ID: {} and user: {}.".format(len(items), list_id, cognito_identity_id)
    return message


def get_items_associated_with_list(table_name, list_id):
    logger.info("Querying table for all items to delete")

    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        logger.info("All items in query response. ({})".format(response['Items']))
    except Exception as e:
        logger.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting lists from table.")

    return response['Items']


def check_request_user_owns_list(cognito_identity_id, items):
    list_owner_item = None
    for item in items:
        if item['SK']['S'].startswith("USER"):
            logger.info("List Owner Item: {}".format(item))
            logger.info("List Owner: {}".format(item['listOwner']['S']))
            list_owner_item = item['listOwner']['S']

    if list_owner_item != cognito_identity_id:
        raise Exception("You are not the owner of this list.")

    return True
