import os
import boto3
import json
from lists import common, logger

log = logger.setup_logger()


def handler(event, context):
    try:
        log.info("Auth Trigger event: " + json.dumps(event))

        user_pool_id = common.get_env_variable(os.environ, 'USERPOOL_ID')
        email = get_email(event)

        if not check_email_verified(event):
            set_email_verified(user_pool_id, email)
    except Exception as e:
        log.error("Exception: {}".format(e))

    return event


def get_email(event):
    try:
        email = event['request']['userAttributes']['email']
    except Exception as e:
        log.error("Exception: {}".format(e))
        raise Exception("Could not get users email as not in event.")

    return email


def check_email_verified(event):
    try:
        log.info("email_verified value: " + event['request']['userAttributes']['email_verified'])
        if event['request']['userAttributes']['email_verified'] != "true":
            return False
    except Exception as e:
        log.error("Exception: {}".format(e))
        raise Exception("Could not get email_verified attribute.")

    return True


def set_email_verified(user_pool_id, email):
    log.info("Updating email_verified for user: " + email)

    try:
        client = boto3.client('cognito-idp')
        client.admin_update_user_attributes(
            UserPoolId=user_pool_id,
            Username=email,
            UserAttributes=[
                {
                    'Name': 'email_verified',
                    'Value': 'true'
                }
            ]
        )
        log.info("Updated email_verified for user: " + email)
    except Exception as e:
        log.error("There was an issue updating email_verified: " + str(e))
        raise Exception("Could not update email_verified attribute.")

    return True
