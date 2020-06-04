import json
import re
from botocore.exceptions import ClientError
import boto3
from urllib.parse import unquote
from lists import common_table_ops, logger
from lists.common_entities import List

log = logger.setup_logger()

ses = boto3.client('ses', region_name='eu-west-1')
SENDER = "Ewelists <contact@ewelists.com>"


def get_env_variable(osenv, name):
    try:
        variable = osenv[name]
        log.info(name + " environment variable value: " + variable)
    except KeyError:
        raise Exception(name + ' environment variable not set correctly.')

    return variable


def get_path_parameter(event, type):
    log.info("Getting path parameter ({}).".format(type))
    if type not in event['pathParameters']:
        raise Exception("Path did not contain a " + type + " parameter.")

    value = event['pathParameters'][type]

    if value == "null":
        raise Exception("Path contained a null " + type + " parameter.")

    value = unquote(value)
    log.info(type + " path parameter: " + value)

    return value


def get_body_attribute(event, type):
    if not event['body']:
        raise Exception("Body was missing required attributes.")

    body_object = json.loads(event['body'])

    if type in body_object:
        value = body_object[type]
    else:
        raise Exception('API Event did not contain a ' + type + ' body attribute.')

    log.info(type + ": " + str(value))
    return value


def parse_email(email):
    email = email.strip()
    email = email.lower()

    return email


def is_google_email(email):
    if '@gmail.com' not in email and '@googlemail.com' not in email:
        return False

    return True


def calculate_new_reserved_quantity(product_item, update_amount):
    new_quantity = product_item['reserved'] + update_amount
    log.info("Product reserved quantity updated from {} to {}".format(product_item['reserved'], new_quantity))

    if new_quantity < 0:
        log.info("Reserved quantity for product ({}) could not be updated by {}.".format(product_item['reserved'], update_amount))
        raise Exception("Reserved quantity for product ({}) could not be updated by {}.".format(product_item['reserved'], update_amount))

    # Think this needs to be new quantity + purchased amount
    if new_quantity + product_item['purchased'] > product_item['quantity']:
        raise Exception("Reserved quantity for product ({}) could not be updated by {} as exceeds required quantity ({}).".format(product_item['reserved'], update_amount, product_item['quantity']))

    return new_quantity


def confirm_owner(table_name, user_id, list_id):
    """Confirms that the user owns a specified list, from the response items relating to a query for the same list."""

    try:
        list_response = common_table_ops.get_list(table_name, user_id, list_id)
    except Exception as e:
        log.info("Error: " + str(e))
        raise Exception("Unexpected error when getting list items from table.")

    if not list_response:
        try:
            common_table_ops.get_list_query(table_name, list_id)
            # Query was succesful, which means list exists, but user is not owner.
            raise Exception("User {} was not owner of List {}.".format(user_id, list_id))
        except Exception as e:
            log.info("Error: " + str(e))
            raise Exception(e)

    log.info("User {} was owner of list {}".format(user_id, list_id))
    return True


def confirm_reservation_owner(reservation_item, user):
    if reservation_item['userId'] != user and reservation_item['email'] != user:
        raise Exception("Requestor is not reservation owner.")
    return True


def create_response(code, body):
    log.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response


def send_email(email, template, template_data):
    log.info("Sending email template {} with data: {}".format(template, template_data))
    try:
        response = ses.send_templated_email(
            Source=SENDER,
            Destination={
                'ToAddresses': [email],
            },
            ReplyToAddresses=[SENDER],
            Template=template,
            TemplateData=json.dumps(template_data)
        )
    except ClientError as e:
        raise Exception("Could not send reserve email: " + e.response['Error']['Message'])
    else:
        log.info("Email sent! Message ID: " + response['MessageId'])

    return True


def get_user(event, osenv, table_name, index_name):
    user = {}

    email = get_path_parameter(event, 'email')
    log.info("Checking if user exists in table with email: " + email)
    user_id = common_table_ops.get_user_id_from_email(table_name, index_name, email)

    if user_id:
        attributes = common_table_ops.get_users_details(table_name, user_id)
        user['exists'] = True
        user['id'] = user_id
        user['email'] = email
        user['name'] = attributes['name']
    else:
        user['exists'] = False
        user['id'] = email
        user['email'] = email

        if event['body']:
            user['name'] = get_body_attribute(event, 'name')

    return user


def get_identity(event, osenv):
    log.info('Getting identity.')
    try:
        userArn = event['requestContext']['identity']['userArn']
        cognito_authentication_provider = event['requestContext']['identity']['cognitoAuthenticationProvider']
    except KeyError:
        raise Exception("There was no identity in the API event.")

    if userArn is None:
        raise Exception("There was no identity in the API event.")

    # Check to see if request was generated by postman, which doesn't authenticate via cognito.
    pattern = re.compile("^arn:aws:iam::[0-9]{12}:user/ApiTestUser$")
    pattern2 = re.compile("^arn:aws:iam::[0-9]{12}:user/ApiTestUser2$")
    if pattern.match(userArn):
        log.info('Request was from postman, using API test identity.')
        identity = get_env_variable(osenv, 'POSTMAN_USERPOOL_SUB')
    elif pattern2.match(userArn):
        log.info('Request was from postman, using API test identity 2.')
        identity = get_env_variable(osenv, 'POSTMAN_USERPOOL_SUB2')
    else:
        identity = cognito_authentication_provider.split(':')[-1]
        log.info('cognitoIdentityId was retrieved from event.')

    return identity


def get_product_type(event):
    try:
        body_object = json.loads(event['body'])
        product_type = body_object['productType']
        log.info("Product type: " + str(product_type))
    except Exception:
        log.error("API Event did not contain the product type in the body.")
        raise Exception('API Event did not contain the product type in the body.')

    if (product_type != 'notfound') and (product_type != 'products'):
        log.error("API Event did not contain a product type of products or notfound.")
        raise Exception('API Event did not contain a product type of products or notfound.')

    return product_type


def gift_is_reserved(item):
    # State of reserved item can only be reserved or purchased.
    if 'state' in item:
        if item['state'] != 'reserved':
            raise Exception("Product was not reserved. State = {}.".format(item['state']))

    return True


def create_product_key(list_id, product_id):
    return {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }


def create_reservation_key(item):
    log.info('Creating resrvation key.')
    return {
        'PK': {'S': "LIST#{}".format(item['listId'])},
        'SK': {'S': "RESERVATION#{}#{}#{}".format(item['productId'], item['userId'], item['reservationId'])}
    }


def check_image_url(url):
    if re.match(r'^//', url):
        url = 'https:' + url

    return url


def get_list_details(table_name, list_id):
    items = common_table_ops.get_list_query(table_name, list_id)

    for item in items:
        if item['SK']['S'].startswith("USER"):
            list = List(item).get_details()

    return list
