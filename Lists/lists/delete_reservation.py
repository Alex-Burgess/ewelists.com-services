import json
import os
import boto3
from lists import common, common_table_ops, logger

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    log.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    response = delete_main(event)
    return response


def delete_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        resv_id_index = common.get_env_variable(os.environ, 'RESERVATIONID_INDEX')
        resv_id = common.get_path_parameter(event, 'id')

        item = common_table_ops.get_reservation(table_name, resv_id_index, resv_id)
        key = common.create_reservation_key(item)

        delete_reservation_item(table_name, key)

    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    data = {'deleted': True}
    response = common.create_response(200, json.dumps(data))
    return response


def delete_reservation_item(table_name, key):
    log.info("Deleting reservation id: {}".format(id))

    try:
        dynamodb.delete_item(
            TableName=table_name,
            Key=key
        )
    except Exception as e:
        log.error("Reservation item could not be deleted: {}".format(e))
        raise Exception('Reservation item could not be deleted.')

    return True
