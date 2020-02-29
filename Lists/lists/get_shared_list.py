import json
import os
import boto3
from lists import common, logger
from lists.common_entities import List, Product, Reserved
from botocore.exceptions import ClientError

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    log.info("event: {}".format(json.dumps(event)))
    response = get_shared_list_main(event)
    return response


def get_shared_list_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        list_id = common.get_path_parameter(event, 'id')
        response_items = get_list_query(table_name, list_id)

        list_object = generate_list_object(response_items)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(list_object))
    return response


def generate_list_object(response_items):
    list = {"list": None, "products": {}, "reserved": {}}

    for item in response_items:
        if item['SK']['S'].startswith("USER"):
            log.info("List Owner Item: {}".format(item))
            list['list'] = List(item).get_details()
        elif item['SK']['S'].startswith("PRODUCT"):
            log.info("Product Item: {}".format(item))
            product = Product(item).get_details()
            productId = product['productId']
            list['products'][productId] = product
        elif item['SK']['S'].startswith("RESERVED"):
            log.info("Reserved Item: {}".format(item))
            reserved = Reserved(item).get_details()
            productId = reserved['productId']
            userId = reserved['userId']

            if productId not in list['reserved']:
                list['reserved'][productId] = {}

            list['reserved'][productId][userId] = reserved

    return list


def get_list_query(table_name, list_id):
    log.info("Querying table {} for list ID {}.".format(table_name, list_id))

    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        log.info("Response: " + json.dumps(response))
    except ClientError as e:
        log.info("get item response: " + json.dumps(e.response))
        raise Exception("Unexpected error when getting list item from table.")

    if len(response['Items']) == 0:
        raise Exception("No query results for List ID {}.".format(list_id))

    return response['Items']
