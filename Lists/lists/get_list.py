import json
import os
import boto3
import logging
from lists import common
from lists import common_env_vars
from lists import common_event
from lists.common_entities import List, Product, Reserved, Shared
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = get_list_main(event)
    return response


def get_list_main(event):
    try:
        table_name = common_env_vars.get_table_name(os.environ)
        identity = common_event.get_identity(event, os.environ)
        list_id = common_event.get_list_id(event)
        response_items = get_list_query(table_name, identity, list_id)
        common.confirm_owner(identity, list_id, response_items)
        list_object = generate_list_object(response_items)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(list_object))
    return response


def generate_list_object(response_items):
    list = {"list": None, "products": {}, "reserved": [], "shared": {}}

    for item in response_items:
        if item['SK']['S'].startswith("USER"):
            logger.info("List Owner Item: {}".format(item))
            list['list'] = List(item).get_details()
        elif item['SK']['S'].startswith("PRODUCT"):
            logger.info("Product Item: {}".format(item))
            product = Product(item).get_details()
            productId = product['productId']
            list['products'][productId] = product
        elif item['SK']['S'].startswith("RESERVED"):
            logger.info("Reserved Item: {}".format(item))
            reserved = Reserved(item).get_details()
            list['reserved'].append(reserved)
        elif item['SK']['S'].startswith("SHARED"):
            if item.get('SK').get('S').split("#")[1] != item['listOwner']['S']:
                logger.info("Shared Item: {}".format(item))
                shared = Shared(item).get_details()
                email = shared['email']
                list['shared'][email] = shared
        elif item['SK']['S'].startswith("PENDING"):
            logger.info("Pending shared Item: {}".format(item))
            shared = Shared(item).get_details()
            email = shared['email']
            list['shared'][email] = shared

    return list


def get_list_query(table_name, cognito_user_id, list_id):
    logger.info("Querying table {} for list ID {} owned by user ID {} .".format(table_name, cognito_user_id, list_id))

    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        logger.info("Response: " + json.dumps(response))
    except ClientError as e:
        logger.info("get item response: " + json.dumps(e.response))
        raise Exception("Unexpected error when getting list item from table.")

    if len(response['Items']) == 0:
        logger.info("No query results for List ID {} and user: {}.".format(list_id, cognito_user_id))
        raise Exception("No query results for List ID {} and user: {}.".format(list_id, cognito_user_id))

    return response['Items']
