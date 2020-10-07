import json
import os
from lists import common, common_table_ops, logger

log = logger.setup_logger()


def handler(event, context):
    log.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    log.info("Body attributes: {}".format(json.dumps(event['body'])))
    response = reservation_main(event)
    return response


def reservation_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        resv_id_index = common.get_env_variable(os.environ, 'RESERVATIONID_INDEX')
        resv_id = common.get_path_parameter(event, 'id')

        item = common_table_ops.get_reservation(table_name, resv_id_index, resv_id)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(item))
    return response
