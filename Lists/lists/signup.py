import os
import boto3
import json
import random
import string
from lists import common, common_kpi, logger

log = logger.setup_logger()

# Email configuration
CHARSET = "UTF-8"
SENDER = "Ewelists <contact@ewelists.com>"


def handler(event, context):
    log.info("SignUp Trigger event: " + json.dumps(event))

    table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
    user_pool_id = common.get_env_variable(os.environ, 'USERPOOL_ID')
    template = common.get_env_variable(os.environ, 'TEMPLATE_NAME')
    domain_name = common.get_env_variable(os.environ, 'DOMAIN_NAME')
    new_user = get_user_from_event(event)
    trigger = get_trigger_source_event(event)

    if common.is_google_email(new_user['email']):
        check_no_alternate_google_email(user_pool_id, new_user['email'])

    exists = get_user_from_userpool(user_pool_id, new_user['email'])

    if exists['exists']:
        log.info("User exists in userpool with email address, linking accounts.")
        link_accounts(user_pool_id, new_user['email'], exists['user_sub'], new_user['type'], new_user['username'])
        raise Exception(new_user['type'] + " LinkedLogon")
    elif trigger == 'PreSignUp_AdminCreateUser':
        log.info("Admin Creating User Account, remember this could be as part of a social signup.")
        create_user_in_lists_db(table_name, new_user['username'], new_user['email'], new_user['name'])

        # Send welcome email
        data = create_email_data(domain_name, new_user['name'])
        common.send_email(new_user['email'], template, data)
    else:
        log.info("User does not have entry in userpool.")

        if new_user['type'] == 'Google' or new_user['type'] == 'Facebook' or new_user['type'] == 'LoginWithAmazon':
            log.info("Creating new cognito user.")

            # Create new cognito user
            new_cognito_user = create_new_cognito_user(user_pool_id, new_user['email'], new_user['name'])
            # Link Accounts
            link_accounts(user_pool_id, new_user['email'], new_cognito_user['user_id'], new_user['type'], new_user['username'])

            # Set random password, otherwise congito account will stay in FORCE_CHANGED_PASSWORD state and user won't be able to reset password.
            set_random_password(user_pool_id, new_user['email'])

            log.info("Completed signup process for user. Raising exception to prevent normal signup process from continuing as not required.")
            common_kpi.post(os.environ, event, 'Users')
            raise Exception(new_user['type'] + " Signup")
        else:
            log.info("New User is using username and password..")
            create_user_in_lists_db(table_name, new_user['username'], new_user['email'], new_user['name'])

            # Send welcome email
            data = create_email_data(domain_name, new_user['name'])
            common.send_email(new_user['email'], template, data)
            common_kpi.post(os.environ, event, 'Users')
            log.info("Allowing signup process to complete for user.")

    return event


def create_email_data(domain_name, name):
    template_data = {
        "name": name,
    }

    return template_data


def set_random_password(user_pool_id, email):
    client = boto3.client('cognito-idp')

    log.info("Using admin_set_user_password to push user out of FORCE_CHANGED_PASSWORD state.")
    password = '!' + ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(12))

    try:
        client.admin_set_user_password(
            UserPoolId=user_pool_id,
            Username=email,
            Password=password,
            Permanent=True
        )
        log.info("Random password for the user set.")

        client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {'Name': 'email_verified', 'Value': 'true'},
            ]
        )
    except Exception as e:
        log.error("There was an issue confirming the users account: " + str(e))

    return True


def create_new_cognito_user(user_pool_id, email, name):
    client = boto3.client('cognito-idp')

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
        log.error("Account could not be created: " + str(e))
        raise Exception('Account creation failed for ' + email + '.')

    log.info("Link response: " + json.dumps(response['User']['Username']))
    log.info("Link response: " + json.dumps(response['User']['Attributes']))

    result['created'] = True
    result['user_id'] = response['User']['Username']

    return result


def link_accounts(user_pool_id, email, existing_sub, new_type, new_id):
    client = boto3.client('cognito-idp')
    log.info("Linking accounts with email {}. {} account ID ({}). Existing user pool identity ({}).".format(email, new_type, new_id, existing_sub))

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
        log.info("Link response: " + json.dumps(response))
    except Exception as e:
        log.error("Accounts could not be joined: " + str(e))
        raise Exception('Accounts could not be joined for ' + email + '.')

    return True


def create_user_in_lists_db(table_name, sub, email, name):
    dynamodb = boto3.client('dynamodb')

    log.info("Creating entry in table {} for user with email {} (sub: {}).".format(table_name, email, sub))

    user_item = {
        'PK': {'S': "USER#{}".format(sub)},
        'SK': {'S': "USER#{}".format(sub)},
        'userId': {'S': sub},
        'email': {'S': email},
    }

    if len(name) > 0:
        user_item['name'] = {'S': name}

    try:
        log.info("Put user item in lists table: {}".format(user_item))
        dynamodb.put_item(TableName=table_name, Item=user_item)
    except Exception as e:
        log.error("User entry could not be created: {}".format(e))
        raise Exception('User entry could not be created for ' + email + '.')

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

    log.info("User object being returned: {}.".format(json.dumps(user)))

    return user


def get_trigger_source_event(event):
    return event['triggerSource']


def check_no_alternate_google_email(user_pool_id, email):
    log.info("Checking if userpool has an entry with similar google mail domains: " + email)

    email = switch_google_domain(email)

    log.info("Checking for: " + email)

    users = get_user_client_call(user_pool_id, email)

    if (len(users)):
        raise Exception('User exists with different google email address ' + email + '.')

    return True


def switch_google_domain(email):
    if '@gmail.com' in email:
        fields = email.split('@')
        email = fields[0] + '@googlemail.com'
    elif '@googlemail.com' in email:
        fields = email.split('@')
        email = fields[0] + '@gmail.com'

    return email


def get_user_client_call(user_pool_id, email):
    client = boto3.client('cognito-idp')

    response = client.list_users(
        UserPoolId=user_pool_id,
        AttributesToGet=['sub', 'email'],
        Limit=10,
        Filter='email ="' + email + '"'
    )

    log.info("Users: {}.".format(response))

    return response['Users']


def get_user_from_userpool(user_pool_id, email):
    log.info("Check if userpool has an entry already for user with email: " + email)

    users = get_user_client_call(user_pool_id, email)

    log.info("Number of users returned {}: ".format(len(users)))

    check_result = {}
    if len(users) > 0:
        log.info("Entry existed in userpool with email {}: {}".format(email, users[0]['Username']))
        log.info("Attributes: {}".format(users[0]['Attributes']))
        check_result['exists'] = True
        check_result['user_sub'] = users[0]['Username']
        check_result['user_attributes'] = users[0]['Attributes']
    else:
        log.info("No entry existed in userpool with email {}.".format(email))
        check_result['exists'] = False

    return check_result
