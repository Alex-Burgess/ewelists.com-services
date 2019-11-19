# A collection of methods that are common across all modules.
import logging
from lists.common_entities import List, Product, Reserved

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


def confirm_owner(user_id, list_id, response_items):
    """Confirms that the user owns a specified list, from the response items relating to a query for the same list."""
    list_owner_id = None
    for item in response_items:
        if item['PK']['S'].startswith("LIST") and item['SK']['S'].startswith("USER"):
            logger.info("List Owner Item: {}".format(item))
            logger.info("List Owner: {}".format(item['listOwner']['S']))
            list_owner_id = item['listOwner']['S']

    if list_owner_id != user_id:
        logger.info("Owner of List ID {} did not match user id of requestor: {}.".format(list_id, user_id))
        raise Exception("Owner of List ID {} did not match user id of requestor: {}.".format(list_id, user_id))

    return True


def confirm_list_shared_with_user(user_id, list_id, response_items):
    shared_user = 'SHARE#' + user_id
    for item in response_items:
        if item['PK']['S'].startswith("LIST") and item['SK']['S'] == shared_user:
            logger.info("Confirmed list {} is shared with user {}".format(list_id, user_id))
            return True

    logger.info("List ID {} did not have a shared item with user {}.".format(list_id, user_id))
    raise Exception("List ID {} did not have a shared item with user {}.".format(list_id, user_id))


def generate_list_object(response_items):
    list = {"list": None, "products": {}, "reserved": []}

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

    return list


def create_response(code, body):
    logger.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response
