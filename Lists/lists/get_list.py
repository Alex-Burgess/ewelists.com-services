import json
import os
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = create_main(event)
    return response


def create_main(event):
    # try:
    #     table_name = get_table_name()
    #     identity = get_identity(event)
    #     listId = generate_list_id(identity['cognitoIdentityId'], table_name)
    #     message = put_item_in_table(table_name, identity['cognitoIdentityId'], identity['userPoolSub'], listId)
    # except Exception as e:
    #     logger.error("Exception: {}".format(e))
    #     response = create_response(500, json.dumps({'error': str(e)}))
    #     logger.info("Returning response: {}".format(response))
    #     return response
    #
    # data = {'listId': listId, 'message': message}

    data = "A list will be returned"

    response = create_response(200, json.dumps(data))
    return response


def create_response(code, body):
    logger.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response
