import os
import boto3
import json
import logging
import random
import string
from lists import common, common_env_vars
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


client = boto3.client('cognito-idp')
dynamodb = boto3.client('dynamodb')
ses = boto3.client('ses', region_name='eu-west-1')

# Email configuration
CHARSET = "UTF-8"
SENDER = "Ewelists <contact@ewelists.com>"


def handler(event, context):
    logger.info("SignUp Trigger event: " + json.dumps(event))

    table_name = common_env_vars.get_table_name(os.environ)
    index_name = common_env_vars.get_table_index(os.environ)
    user_pool_id = common_env_vars.get_userpool_id(os.environ)
    template = get_template_name(os.environ)
    new_user = get_user_from_event(event)
    trigger = get_trigger_source_event(event)
    exists = get_user_from_userpool(user_pool_id, new_user['email'])

    if exists['exists']:
        logger.info("User exists in userpool.")
        link_accounts(user_pool_id, new_user['email'], exists['user_sub'], new_user['type'], new_user['username'])
        raise Exception("Linked new account to existing user account matching on email address.")
    elif trigger == 'PreSignUp_AdminCreateUser':
        logger.info("Admin Creating User Account, remember this could be as part of a social signup.")
        create_user_in_lists_db(table_name, new_user['username'], new_user['email'], new_user['name'])

        # Send welcome email
        send(new_user['email'], new_user['name'], template)
    else:
        logger.info("User does not have entry in userpool.")

        if new_user['type'] == 'Google' or new_user['type'] == 'Facebook' or new_user['type'] == 'LoginWithAmazon':
            logger.info("Creating new cognito user.")

            # Create new cognito user
            new_cognito_user = create_new_cognito_user(user_pool_id, new_user['email'], new_user['name'])
            # Link Accounts
            link_accounts(user_pool_id, new_user['email'], new_cognito_user['user_id'], new_user['type'], new_user['username'])

            # Get all the pending shared lists
            pending_lists = get_pending_lists(table_name, index_name, new_user['email'])

            # Transaction to delete pending item and add SHARED item
            if len(pending_lists) > 0:
                create_shared_items(table_name, pending_lists, new_user['username'], new_user['name'])

            # Set random password, otherwise congito account will stay in FORCE_CHANGED_PASSWORD state and user won't be able to reset password.
            set_random_password(user_pool_id, new_user['email'])

            logger.info("Completed signup process for user. Raising exception to prevent normal signup process from continuing as not required.")
            raise Exception("Sign up process complete for user.")
        else:
            logger.info("New User is using username and password..")
            create_user_in_lists_db(table_name, new_user['username'], new_user['email'], new_user['name'])

            # Get all the pending shared lists
            pending_lists = get_pending_lists(table_name, index_name, new_user['email'])

            if len(pending_lists) > 0:
                create_shared_items(table_name, pending_lists, new_user['username'], new_user['name'])

            # Send welcome email
            send(new_user['email'], new_user['name'], template)
            logger.info("Allowing signup process to complete for user.")

    return event


def get_template_name(osenv):
    try:
        name = osenv['TEMPLATE_NAME']
        logger.info("TEMPLATE_NAME environment variable value: " + name)
    except KeyError:
        raise Exception('TEMPLATE_NAME environment variable not set correctly.')

    return name


def send(email, name, template):
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


def get_pending_lists(table_name, index_name, email):
    try:
        response = dynamodb.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression="SK = :SK",
            ExpressionAttributeValues={":SK":  {'S': "PENDING#" + email}}
        )
        logger.info("All items in query response. ({})".format(response['Items']))
    except Exception as e:
        logger.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting pending lists from table.")

    return response['Items']


def create_shared_items(table_name, pending_items, sub, name):
    for pending_list in pending_items:
        pending_key = {
            'PK': {'S': pending_list['PK']['S']},
            'SK': {'S': pending_list['SK']['S']}
        }

        delete_condition = {
            ':PK': {'S': pending_list['PK']['S']},
            ':SK': {'S': pending_list['SK']['S']}
        }

        shared_item = pending_list
        shared_item['SK'] = {'S': 'SHARED#' + sub}
        shared_item['userId'] = {'S': sub}
        shared_item['shared_user_name'] = {'S': name}

        try:
            response = dynamodb.transact_write_items(
                TransactItems=[
                    {
                        'Put': {
                            'TableName': table_name,
                            'Item': shared_item
                        }
                    },
                    {
                        'Delete': {
                            'TableName': table_name,
                            'Key': pending_key,
                            'ConditionExpression': "PK = :PK AND SK = :SK",
                            'ExpressionAttributeValues': delete_condition
                        }
                    }
                ]
            )
            logger.info("Attributes updated: " + json.dumps(response))
        except Exception as e:
            logger.info("Transaction write exception: " + str(e))
            raise Exception("Unexpected error when unreserving product.")

    return True


def set_random_password(user_pool_id, email):
    logger.info("Using admin_set_user_password to push user out of FORCE_CHANGED_PASSWORD state.")
    password = '!' + ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(12))

    try:
        client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=email,
            Password=password,
            Permanent=True
        )
        logger.info("Random password for the user set.")

        client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {'Name': 'email_verified', 'Value': 'true'},
            ]
        )
    except Exception as e:
        logger.error("There was an issue confirming the users account: " + str(e))

    return True


def create_new_cognito_user(user_pool_id, email, name):
    result = {}

    try:
        response = client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'name', 'Value': name},
            ],
            MessageAction='SUPPRESS',
        )
    except Exception as e:
        logger.error("Account could not be created: " + str(e))
        raise Exception('Account could not be created.')

    logger.info("Link response: " + json.dumps(response['User']['Username']))
    logger.info("Link response: " + json.dumps(response['User']['Attributes']))

    result['created'] = True
    result['user_id'] = response['User']['Username']

    return result


def link_accounts(user_pool_id, email, existing_sub, new_type, new_id):
    logger.info("Linking accounts with email {}. {} account ID ({}). Existing user pool identity ({}).".format(email, new_type, new_id, existing_sub))

    try:
        response = client.admin_link_provider_for_user(
            UserPoolId=user_pool_id,
            DestinationUser={
                'ProviderName': 'Cognito',
                'ProviderAttributeName': 'Username',
                'ProviderAttributeValue': existing_sub
            },
            SourceUser={
                'ProviderName': new_type,
                'ProviderAttributeName': 'Cognito_Subject',
                'ProviderAttributeValue': new_id
            }
        )
        logger.info("Link response: " + json.dumps(response))
    except Exception as e:
        logger.error("Accounts could not be joined: " + str(e))
        raise Exception('Accounts could not be joined.')

    return True


def create_user_in_lists_db(table_name, sub, email, name):
    logger.info("Creating entry in table {} for user with email {} (sub: {}).".format(table_name, email, sub))

    user_item = {
        'PK': {'S': "USER#{}".format(sub)},
        'SK': {'S': "USER#{}".format(sub)},
        'userId': {'S': sub},
        'email': {'S': email},
    }

    if len(name) > 0:
        user_item['name'] = {'S': name}

    try:
        logger.info("Put user item in lists table: {}".format(user_item))
        dynamodb.put_item(TableName=table_name, Item=user_item)
    except Exception as e:
        logger.error("User entry could not be created: {}".format(e))
        raise Exception('User entry could not be created.')

    return True


def get_user_from_event(event):
    user = {}

    user['email'] = common.parse_email(event['request']['userAttributes']['email'])

    if 'name' in event['request']['userAttributes']:
        user['name'] = event['request']['userAttributes']['name']
    else:
        user['name'] = ''

    if "Google" in event['userName'] or "Facebook" in event['userName']:
        user['type'] = event['userName'].split('_')[0]
        user['username'] = event['userName'].split('_')[-1]
    elif "LoginWithAmazon" in event['userName']:
        user['type'] = event['userName'].split('_')[0]
        user['username'] = 'amzn1.account.' + event['userName'].split('.')[-1]
    else:
        user['type'] = "Cognito"
        user['username'] = event['userName']

    logger.info("User object being returned: {}.".format(json.dumps(user)))

    return user


def get_trigger_source_event(event):
    return event['triggerSource']


def get_user_from_userpool(user_pool_id, email):
    logger.info("Check if userpool has an entry already for user with email: " + email)

    response = client.list_users(
        UserPoolId=user_pool_id,
        AttributesToGet=[
            'sub',
            'email'
        ],
        Limit=10,
        Filter='email ="' + email + '"'
    )

    logger.info("Number of users returned {}: ".format(len(response['Users'])))

    check_result = {}
    if len(response['Users']) > 0:
        logger.info("Entry existed in userpool with email {}: {}".format(email, response['Users'][0]['Username']))
        logger.info("Attributes: {}".format(response['Users'][0]['Attributes']))
        check_result['exists'] = True
        check_result['user_sub'] = response['Users'][0]['Username']
        check_result['user_attributes'] = response['Users'][0]['Attributes']
    else:
        logger.info("No entry existed in userpool with email {}.".format(email))
        check_result['exists'] = False

    return check_result
