import json
import os
import boto3
from lists import common, common_table_ops, logger
from lists.common_entities import List, Product, Reservation

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
        response_items = common_table_ops.get_list_query(table_name, list_id)

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
        elif item['SK']['S'].startswith("RESERVATION") and item['state']['S'] != 'cancelled':
            log.info("Reserved Item: {}".format(item))
            reserved = Reservation(item).get_details()
            productId = reserved['productId']
            userId = reserved['userId']

            if productId not in list['reserved']:
                list['reserved'][productId] = {}

            if userId not in list['reserved'][productId]:
                list['reserved'][productId][userId] = []

            list['reserved'][productId][userId].append(reserved)

    return list
