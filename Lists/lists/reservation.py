import json
import os
import boto3
from botocore.exceptions import ClientError
from lists import common, logger
from lists.common_entities import Reservation

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    log.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    log.info("Body attributes: {}".format(json.dumps(event['body'])))
    response = reservation_main(event)
    return response


def reservation_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        resv_id = common.get_path_parameter(event, 'id')

        item = get_reservation(table_name, resv_id)

        data = Reservation(item).get_details()
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(data))
    return response


def get_reservation(table_name, id):
    log.info("Querying table {} for reservation ID {}.".format(table_name, id))

    key = {
        'PK': {'S': "RESERVATION#" + id},
        'SK': {'S': "RESERVATION#" + id}
    }

    try:
        response = dynamodb.get_item(
            TableName=table_name,
            Key=key
        )
    except ClientError as e:
        log.error("Get item response: " + json.dumps(e.response))
        raise Exception("Unexpected error when getting reservation item from table.")

    if 'Item' not in response:
        raise Exception("Reservation ID {} did not exist.".format(id))

    log.info("Reservation item: {}.".format(response['Item']))

    return response['Item']
