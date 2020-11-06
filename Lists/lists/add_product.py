import json
import os
import boto3
from lists import common, common_kpi, logger
from botocore.exceptions import ClientError

log = logger.setup_logger()


def handler(event, context):
    response = add_product_main(event)
    return response


def add_product_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common.get_identity(event, os.environ)
        list_id = common.get_path_parameter(event, 'id')
        product_id = common.get_path_parameter(event, 'productid')
        quantity = common.get_body_attribute(event, 'quantity')
        type = common.get_product_type(event)
        notes = get_notes(event)
        common.confirm_owner(table_name, identity, list_id)

        message = create_product_item(table_name, list_id, product_id, type, quantity, notes)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    common_kpi.post(os.environ, event, 'Gifts Added')

    data = {'message': message}
    response = common.create_response(200, json.dumps(data))
    return response


def get_notes(event):
    if not event['body']:
        raise Exception("Body was missing required attributes.")

    body_object = json.loads(event['body'])

    if 'notes' in body_object:
        value = body_object['notes']
    else:
        value = None

    log.info("Notes: " + str(value))
    return value


def create_product_item(table_name, list_id, product_id, type, quantity, notes):
    dynamodb = boto3.client('dynamodb')

    item = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)},
        'type': {'S': type},
        'quantity': {'N': str(quantity)},
        'reserved': {'N': str(0)},
        'purchased': {'N': str(0)}
    }

    if notes:
        item['notes'] = {'S': notes}

    try:
        log.info("Put product item: {}".format(item))
        response = dynamodb.put_item(
            TableName=table_name,
            Item=item,
            ConditionExpression='attribute_not_exists(PK)'
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            log.info("Product {} already exists in list {}.".format(product_id, list_id))
            raise Exception("Product already exists in list.")
        else:
            log.error("Product could not be created: {}".format(e))
            raise Exception('Product could not be created.')

    log.info("Add response: {}".format(response))

    return True
