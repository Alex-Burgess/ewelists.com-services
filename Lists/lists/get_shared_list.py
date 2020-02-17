import json
import os
import boto3
import logging
from lists import common
from lists import common_env_vars
from lists import common_event
from lists.common_entities import List, Product, Reserved
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    logger.info("event: {}".format(json.dumps(event)))
    response = get_shared_list_main(event)
    return response


def get_shared_list_main(event):
    try:
        table_name = common_env_vars.get_table_name(os.environ)
        list_id = common_event.get_list_id(event)
        response_items = get_list_query(table_name, list_id)

        list_object = generate_shared_list_object(response_items)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(list_object))
    return response


def generate_shared_list_object(response_items):
    list = {"list": None, "products": {}, "reserved": {}}

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
            productId = reserved['productId']
            userId = reserved['userId']

            if productId not in list['reserved']:
                list['reserved'][productId] = {}

            list['reserved'][productId][userId] = reserved

    return list


def get_list_query(table_name, list_id):
    logger.info("Querying table {} for list ID {}.".format(table_name, list_id))

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
        raise Exception("No query results for List ID {}.".format(list_id))

    return response['Items']
