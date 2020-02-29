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
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common.get_identity(event, os.environ)
        list_id = common.get_path_parameter(event, 'id')
        items = get_items_associated_with_list(table_name, list_id)
        common.confirm_owner(identity, list_id, items)
        delete_items(table_name, identity, list_id, items)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'deleted': True, 'listId': list_id, "count": len(items)}

    response = common.create_response(200, json.dumps(data))
    return response


def delete_items(table_name, cognito_user_id, list_id, items):
    logger.info("Deleting List ID: {} for user: {}.".format(list_id, cognito_user_id))

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
                logger.info("Delete request failed for List ID: {} and user {} as condition check for List ID failed.  List does not exist.".format(list_id, cognito_user_id))
                raise Exception("List does not exist.")
            else:
                raise

    logger.info("Deleted all items [{}] for List ID: {} and user: {}.".format(len(items), list_id, cognito_user_id)),
    return True


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

    if len(response['Items']) == 0:
        logger.info("No items for the list {} were found.".format(list_id))
        raise Exception("No list exists with this ID.")

    return response['Items']
