import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


client = boto3.client('cognito-idp')
dynamodb = boto3.client('dynamodb')


def handler(event, context):
    logger.info("SignUp Post Confirmation Trigger event: " + json.dumps(event))

    logger.info("Creating entry in table {}: " + json.dumps(event))

    user = get_user_sub(event['userName'])

    user_atts = {}
    for attribute in user['UserAttributes']:
        attribute_name = attribute['Name']
        attribute_value = attribute['Value']
        user_atts[attribute_name] = attribute_value

    logger.info("User sub: " + user_atts['sub'])
    logger.info("User email: " + user_atts['email'])

    userId = user_atts['sub']
    email = user_atts['email']

    table_name = 'lists-test'
    user_item = {
        'PK': {'S': "USER#{}".format(userId)},
        'SK': {'S': "USER#{}".format(userId)},
        'userId': {'S': userId},
        'email': {'S': email}
    }

    try:
        logger.info("Put user item in lists table: {}".format(user_item))
        dynamodb.put_item(TableName=table_name, Item=user_item)
    except Exception as e:
        logger.error("User entry could not be created: {}".format(e))

    return event


def get_user_sub(username):
    logger.info("Get sub for user: " + username)

    response = client.admin_get_user(
        UserPoolId='eu-west-1_vqox9Z8q7',
        Username=username
    )

    logger.info("User entry returned.  sub: " + json.dumps(response['UserAttributes']))
    # logger.info("User entry returned.  sub: " + response['UserAttributes']['sub'])

    return response
