import json
import os
import boto3
import time
import logging
from lists import common
from lists import common_table_ops
from lists import common_event
from lists.common_entities import User
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')
ses = boto3.client('ses', region_name='eu-west-1')

# Email configuration
CHARSET = "UTF-8"
SENDER = "Ewelists <contact@ewelists.com>"


def handler(event, context):
    response = share_main(event)
    return response


def share_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        index_name = common.get_env_variable(os.environ, 'INDEX_NAME')
        domain_name = common.get_env_variable(os.environ, 'DOMAIN_NAME')
        identity = common_event.get_identity(event, os.environ)
        list_id = common_event.get_list_id(event)
        email = common_event.get_path_parameter(event, 'user')
        email = common.parse_email(email)
        list = common_table_ops.get_list(table_name, identity, list_id)
        list_owner_name = common_table_ops.get_users_details(table_name, identity)['name']
        common.confirm_owner(identity, list_id, [list])

        user = get_user_if_exists(table_name, index_name, email)

        subject = email_subject(list_owner_name)

        if user:
            create_shared_entry(table_name, user, list)
            share_exists_url = exist_url(domain_name, list_id)
            body_text = shared_email_text(user['name'], list_owner_name, list['title']['S'], share_exists_url)
            body_html = shared_email_html(user['name'], list_owner_name, list['title']['S'], share_exists_url)
            send_email(email, body_text, body_html, subject)

            data = {
                'user': {'userId': user['userId'], 'email': email, 'name': user['name'], 'type': 'SHARED'}
            }
        else:
            create_pending_entry(table_name, email, list)
            share_signup_url = signup_url(domain_name, list_id)
            body_text = pending_email_text(list_owner_name, list['title']['S'], share_signup_url)
            body_html = pending_email_html(list_owner_name, list['title']['S'], share_signup_url)
            send_email(email, body_text, body_html, subject)

            data = {
                'user': {'email': email, 'type': 'PENDING'}
            }
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(data))
    return response


def exist_url(url, id):
    list_url = url + "/lists/" + id
    logger.info("User exists share url: " + list_url)
    return list_url


def signup_url(url, id):
    list_url = url + "/signup?redirect=/lists/" + id
    logger.info("Signup share url: " + list_url)
    return list_url


def email_subject(list_owner_name):
    subject = list_owner_name + " shared a gift list with you!"
    logger.info("Email subject: " + subject)
    return subject


def pending_email_text(list_owner_name, list_title, url):
    body_text = ("Hi,\r\n" + list_owner_name + " shared " + list_title + " with you on Ewelists.\r\n"
                 "You can view this list by signing up at " + url
                 )

    return body_text


def pending_email_html(list_owner_name, list_title, url):
    body_html = "<html><head></head><body>"
    body_html += "<p>Hi,</p>"
    body_html += "<p>" + list_owner_name + " shared " + list_title + " with you on Ewelists.</p>"
    body_html += "You can view this list by signing up at <a href=\"" + url + "\">Ewelists</a>"
    body_html += "</body></html>"

    return body_html


def shared_email_text(recipient_name, list_owner_name, list_title, url):
    body_text = ("Hi " + recipient_name + ",\r\n" + list_owner_name + " shared " + list_title + " with you on Ewelists.\r\n"
                 "You can view this list by signing up at " + url
                 )

    return body_text


def shared_email_html(recipient_name, list_owner_name, list_title, url):
    body_html = "<html><head></head><body>"
    body_html += "<h3>Hi " + recipient_name + ",</h3>"
    body_html += "<p>" + list_owner_name + " shared " + list_title + " with you on Ewelists.</p>"
    body_html += "<a href=\"" + url + "\">View List</a>"
    body_html += "</body></html>"

    return body_html


def send_email(recipient, body_text, body_html, subject):
    try:
        response = ses.send_email(
            Destination={
                'ToAddresses': [recipient],
            },
            Message={
                'Body': {
                    'Html': {'Charset': CHARSET, 'Data': body_html},
                    'Text': {'Charset': CHARSET, 'Data': body_text},
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


def get_user_if_exists(table_name, index_name, email):
    try:
        response = dynamodb.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression="email = :email",
            ExpressionAttributeValues={":email":  {'S': email}}
        )
    except Exception as e:
        logger.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting user from table.")

    if 'Items' not in response:
        logger.info("No user with email {} was found.".format(email))
        return {}

    if len(response['Items']) == 0:
        logger.info("No user with email {} was found.".format(email))
        return {}

    logger.info("All items in query response. ({})".format(response['Items']))

    return User(response['Items'][0]).get_basic_details()


def create_shared_entry(table_name, user, list):
    item = {
        'PK': {'S': "LIST#{}".format(list['listId']['S'])},
        'SK': {'S': "SHARED#{}".format(user['userId'])},
        'listId': {'S': list['listId']['S']},
        'listOwner': {'S': list['listOwner']['S']},
        'userId': {'S': user['userId']},
        'shared_user_name': {'S': user['name']},
        'shared_user_email': {'S': user['email']},
        'title': {'S': list['title']['S']},
        'occasion': {'S': list['occasion']['S']},
        'description': {'S': list['description']['S']},
        'createdAt': {'N': str(int(time.time()))},
        'imageUrl': {'S': list['imageUrl']['S']},
    }

    try:
        logger.info("Put shared item for lists table: {}".format(item))
        response = dynamodb.put_item(
            TableName=table_name,
            Item=item,
            ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            logger.info("List {} already shared with user {}.".format(list['listId'], user['userId']))
            raise Exception("User already exists in list.")
        else:
            logger.error("Shared item could not be created: {}".format(e))
            raise Exception('Shared item could not be created.')

    logger.info("Create response: {}".format(json.dumps(response)))

    return True


def create_pending_entry(table_name, email, list):
    item = {
        'PK': {'S': "LIST#{}".format(list['listId']['S'])},
        'SK': {'S': "PENDING#{}".format(email)},
        'listId': {'S': list['listId']['S']},
        'listOwner': {'S': list['listOwner']['S']},
        'title': {'S': list['title']['S']},
        'shared_user_email': {'S': email},
        'occasion': {'S': list['occasion']['S']},
        'description': {'S': list['description']['S']},
        'createdAt': {'N': str(int(time.time()))},
        'imageUrl': {'S': list['imageUrl']['S']},
    }

    try:
        logger.info("Put shared item for lists table: {}".format(item))
        response = dynamodb.put_item(
            TableName=table_name,
            Item=item,
            ConditionExpression="attribute_not_exists(PK) AND attribute_not_exists(SK)",
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            logger.info("List {} already shared with user {}.".format(list['listId'], email))
            raise Exception("User already exists in list.")
        else:
            logger.error("Shared item could not be created: {}".format(e))
            raise Exception('Shared item could not be created.')

    logger.info("Create response: {}".format(json.dumps(response)))

    return True
