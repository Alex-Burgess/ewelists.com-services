# A collection of methods that are common across all modules.
import logging
import boto3
from lists import common_event
from lists import common_table_ops
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


# Email configuration
ses = boto3.client('ses', region_name='eu-west-1')
SENDER = "Ewelists <contact@ewelists.com>"


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
        user['id'] = common_event.get_path_parameter(event, 'email')
        user['email'] = common_event.get_path_parameter(event, 'email')
        user['name'] = common_event.get_body_attribute(event, 'name')
        user['exists'] = False
    else:
        user['id'] = common_event.get_identity(event, osenv)
        attributes = common_table_ops.get_users_details(table_name, user['id'])
        user['email'] = attributes['email']
        user['name'] = attributes['name']
        user['exists'] = True

    return user
