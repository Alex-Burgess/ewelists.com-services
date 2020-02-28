# A collection of methods that are common across all modules.
import logging
import json
import re
from botocore.exceptions import ClientError
import boto3
from urllib.parse import unquote
from lists import common_table_ops

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


# Email configuration
ses = boto3.client('ses', region_name='eu-west-1')
SENDER = "Ewelists <contact@ewelists.com>"


def get_env_variable(osenv, name):
    try:
        variable = osenv[name]
        logger.info(name + " environment variable value: " + variable)
    except KeyError:
        raise Exception(name + ' environment variable not set correctly.')

    return variable


def get_path_parameter(event, type):
    if type not in event['pathParameters']:
        raise Exception("Path did not contain a " + type + " parameter.")

    value = event['pathParameters'][type]

    if value == "null":
        raise Exception("Path contained a null " + type + " parameter.")

    value = unquote(value)
    logger.info(type + " path parameter: " + value)

    return value


def get_body_attribute(event, type):
    if not event['body']:
        raise Exception("Body was missing required attributes.")

    body_object = json.loads(event['body'])

    if type in body_object:
        value = body_object[type]
    else:
        raise Exception('API Event did not contain a ' + type + ' body attribute.')

    logger.info(type + ": " + str(value))
    return value


def parse_email(email):
    email = email.strip()
    email = email.lower()

    if '@googlemail.com' in email:
        fields = email.split('@')
        email = fields[0] + '@gmail.com'

    return email


def calculate_new_reserved_quantity(product_item, update_amount):
    new_quantity = product_item['reserved'] + update_amount
    logger.info("Product reserved quantity updated from {} to {}".format(product_item['reserved'], new_quantity))

    if new_quantity < 0:
        logger.info("Reserved quantity for product ({}) could not be updated by {}.".format(product_item['reserved'], update_amount))
        raise Exception("Reserved quantity for product ({}) could not be updated by {}.".format(product_item['reserved'], update_amount))

    if new_quantity > product_item['quantity']:
        raise Exception("Reserved quantity for product ({}) could not be updated by {} as exceeds required quantity ({}).".format(product_item['reserved'], update_amount, product_item['quantity']))

    return new_quantity


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
    shared_user = 'SHARED#' + user_id
    for item in response_items:
        if item['PK']['S'].startswith("LIST") and item['SK']['S'] == shared_user:
            logger.info("Confirmed list {} is shared with user {}".format(list_id, user_id))
            return True

    logger.info("List ID {} did not have a shared item with user {}.".format(list_id, user_id))
    raise Exception("List ID {} did not have a shared item with user {}.".format(list_id, user_id))


def create_response(code, body):
    logger.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response


def send_email(email, name, template):
    try:
        response = ses.send_templated_email(
            Source=SENDER,
            Destination={
                'ToAddresses': [email],
            },
            ReplyToAddresses=[SENDER],
            Template=template,
            TemplateData='{ \"name\":\"' + name + '\" }'
        )
    except ClientError as e:
        raise Exception("Could not send welcome email: " + e.response['Error']['Message'])
    else:
        logger.info("Email sent! Message ID: " + response['MessageId'])

    return True


def get_user(event, osenv, table_name):
    user = {}

    if 'email' in event['pathParameters']:
        user['id'] = get_path_parameter(event, 'email')
        user['email'] = get_path_parameter(event, 'email')
        user['name'] = get_body_attribute(event, 'name')

        user['exists'] = False
    else:
        user['id'] = get_identity(event, osenv)
        attributes = common_table_ops.get_users_details(table_name, user['id'])
        user['email'] = attributes['email']
        user['name'] = attributes['name']
        user['exists'] = True

    return user


# TODO - delete when delete share modules.
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


def get_identity(event, osenv):
    try:
        userArn = event['requestContext']['identity']['userArn']
        user_id = event['requestContext']['identity']['cognitoIdentityId']
        cognito_authentication_provider = event['requestContext']['identity']['cognitoAuthenticationProvider']
    except KeyError:
        logger.error("There was no identity context in API event.")
        raise Exception("There was no identity context in API event.")

    # Check to see if request was generated by postman, which doesn't authenticate via cognito.
    pattern = re.compile("^arn:aws:iam::[0-9]{12}:user/ApiTestUser$")
    pattern2 = re.compile("^arn:aws:iam::[0-9]{12}:user/ApiTestUser2$")
    if pattern.match(userArn):
        logger.info('Request was from postman, using API test identity.')
        identity = get_env_variable(osenv, 'POSTMAN_USERPOOL_SUB')
    elif pattern2.match(userArn):
        logger.info('Request was from postman, using API test identity 2.')
        identity = get_env_variable(osenv, 'POSTMAN_USERPOOL_SUB2')
    else:
        if user_id is None:
            raise Exception("There was no cognitoIdentityId in the API event.")

        identity = cognito_authentication_provider.split(':')[-1]
        logger.info('cognitoIdentityId was retrieved from event.')

    return identity
