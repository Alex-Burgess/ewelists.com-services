import logging
import re
import json
from lists import common_env_vars
from urllib.parse import unquote

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


def get_identity(event, osenv):

    try:
        userArn = event['requestContext']['identity']['userArn']
        user_id = event['requestContext']['identity']['cognitoIdentityId']
        cognito_authentication_provider = event['requestContext']['identity']['cognitoAuthenticationProvider']
    except KeyError:
        logger.error("There was no identity context in API event.")
        raise Exception("There was no identity context in API event.")

    # Check to see if request was generated by postman, which doesn't authenticate via cognito.
    pattern = re.compile("^arn:aws:iam::[0-9]{12}:user/ApiTestUser")
    if pattern.match(userArn):
        logger.info('Request was from postman, using API test identity.')
        identity = common_env_vars.get_postman_identity(osenv)
    else:
        if user_id is None:
            raise Exception("There was no cognitoIdentityId in the API event.")

        identity = cognito_authentication_provider.split(':')[-1]

        logger.info('cognitoIdentityId was retrieved from event.')

    return identity


def get_list_id(event):
    try:
        list_id = event['pathParameters']['id']
        logger.info("List ID: " + list_id)
    except Exception:
        logger.error("API Event did not contain a List ID in the path parameters.")
        raise Exception('API Event did not contain a List ID in the path parameters.')

    if len(list_id) == 0:
        logger.error("List ID was empty.")
        raise Exception('API Event did not contain a List ID in the path parameters.')

    return list_id


def get_product_id(event):
    try:
        product_id = event['pathParameters']['productid']
        logger.info("Product ID: " + product_id)
    except Exception:
        logger.error("API Event did not contain a Product ID in the path parameters.")
        raise Exception('API Event did not contain a Product ID in the path parameters.')

    if len(product_id) == 0:
        logger.error("Product ID was empty.")
        raise Exception('API Event did not contain a Product ID in the path parameters.')

    return product_id


def get_user(event):
    try:
        user = event['pathParameters']['user']
        logger.info("User parameter: " + user)
    except Exception:
        logger.error("API Event did not contain an user in the path parameters.")
        raise Exception('API Event did not contain a user in the path parameters.')

    if len(user) == 0:
        logger.error("List ID was empty.")
        raise Exception('API Event did not contain a user in the path parameters.')

    user = unquote(user)
    logger.info("Decoded email: " + user)

    return user


def get_quantity(event):
    try:
        body_object = json.loads(event['body'])
        quantity = body_object['quantity']
        logger.info("Quantity: " + str(quantity))
    except Exception:
        logger.error("API Event did not contain the quantity in the body.")
        raise Exception('API Event did not contain the quantity in the body.')

    return quantity


def get_product_type(event):
    try:
        body_object = json.loads(event['body'])
        product_type = body_object['productType']
        logger.info("Product type: " + str(product_type))
    except Exception:
        logger.error("API Event did not contain the product type in the body.")
        raise Exception('API Event did not contain the product type in the body.')

    if (product_type != 'notfound') and (product_type != 'products'):
        logger.error("API Event did not contain a product type of products or notfound.")
        raise Exception('API Event did not contain a product type of products or notfound.')

    return product_type


def get_share_type(event):
    try:
        body_object = json.loads(event['body'])
        share_type = body_object['share_type']
        logger.info("Product type: " + str(share_type))
    except Exception:
        logger.error("API Event did not contain a share type in the body.")
        raise Exception('API Event did not contain a share type in the body.')

    if (share_type != 'SHARED') and (share_type != 'PENDING'):
        logger.error("API Event did not contain a share type of SHARED or PENDING.")
        raise Exception('API Event did not contain a share type of SHARED or PENDING.')

    return share_type


def get_message(event):
    try:
        body_object = json.loads(event['body'])
        message = body_object['message']
        logger.info("Message: " + message)
    except Exception:
        logger.error("API Event did not contain a message in the body.")
        raise Exception('API Event did not contain a message in the body.')

    return message