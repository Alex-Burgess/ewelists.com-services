import os
import json
import boto3
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))

ses = boto3.client('ses', region_name='eu-west-1')

# Email configuration
CHARSET = "UTF-8"
SENDER = "Ewelists <contact@ewelists.com>"


def handler(event, context):
    try:
        name = get_sender_details(event, 'name')
        email = get_sender_details(event, 'email')
        template = get_template_name(os.environ)
        send(email, name, template)
    except Exception as e:
        logger.error("Exception: {}".format(e))

    return event


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


def get_sender_details(event, attribute):
    try:
        value = event['request']['userAttributes'][attribute]
        logger.info(attribute + ": " + str(value))
    except Exception:
        logger.error("Event did not contain user attributes: " + json.dumps(event))
        raise Exception("Could not send welcome email. API Event did not contain " + attribute + " in the body.")

    return value


def get_template_name(osenv):
    try:
        name = osenv['TEMPLATE_NAME']
        logger.info("TEMPLATE_NAME environment variable value: " + name)
    except KeyError:
        raise Exception('TEMPLATE_NAME environment variable not set correctly.')

    return name
