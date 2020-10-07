import json
import boto3
import logging
from random import randint
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))

# Email configuration
CHARSET = "UTF-8"
RECEIVER = "Ewelists <contact@ewelists.com>"
SENDER = "Ewelists <contact@ewelists.com>"


def handler(event, context):
    response = contact_main(event)
    return response


def contact_main(event):
    try:
        name = get_sender_details(event, 'name')
        email = get_sender_details(event, 'email')
        message_id = get_id()
        subject = get_subject(name, message_id)
        message = get_sender_details(event, 'message')

        body = html_body(name, email, message)
        send(body, subject)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'name': name, 'email': email, 'message': message, 'id': message_id}
    response = create_response(200, json.dumps(data))
    return response


def get_id():
    return randint(100000, 999999)


def send(body_html, subject):
    ses = boto3.client('ses', region_name='eu-west-1')

    try:
        response = ses.send_email(
            Destination={
                'ToAddresses': [RECEIVER],
            },
            Message={
                'Body': {
                    'Html': {'Charset': CHARSET, 'Data': body_html},
                    # 'Text': {'Charset': CHARSET, 'Data': body_text},
                },
                'Subject': {'Charset': CHARSET, 'Data': subject},
            },
            Source=SENDER
        )
    except ClientError as e:
        logger.error("Error sending email: " + e.response['Error']['Message'])
        raise Exception("Error sending email: " + e.response['Error']['Message'])
    else:
        logger.info("Email sent! Message ID: " + response['MessageId'])

    return True


def html_body(name, email, message):
    body_html = "<html><head></head><body>"
    body_html += "Name: " + name
    body_html += "<br />Email: " + email
    body_html += "<br />Message:"
    body_html += "<p>" + message + "</p>"
    body_html += "</body></html>"

    return body_html


def get_subject(name, id):
    return "Ewemail from " + name + ". #" + str(id)


def get_sender_details(event, attribute):
    try:
        body = json.loads(event['body'])
        value = body[attribute]
        logger.info(attribute + ": " + str(value))
    except Exception:
        raise Exception("API Event did not contain " + attribute + " in the body.")

    return value


def create_response(code, body):
    logger.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response
