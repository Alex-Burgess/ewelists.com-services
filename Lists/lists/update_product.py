import json
import os
import boto3
from lists import common, logger
from botocore.exceptions import ClientError

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = update_product_main(event)
    return response


def update_product_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common.get_identity(event, os.environ)
        list_id = common.get_path_parameter(event, 'id')
        product_id = common.get_path_parameter(event, 'productid')
        quantity = common.get_body_attribute(event, 'quantity')
        common.confirm_owner(table_name, identity, list_id)

        quantity = update_product_item(table_name, list_id, product_id, quantity)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    data = {'quantity': quantity}
    response = common.create_response(200, json.dumps(data))
    return response


def update_product_item(table_name, list_id, product_id, quantity):
    key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    try:
        log.info("Updating quantity of product item ({}) to {}".format(key, quantity))
        response = dynamodb.update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression="set quantity = :q",
            ExpressionAttributeValues={
                ':q': {'N': str(quantity)},
            },
            ConditionExpression="attribute_exists(PK)",
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        log.error("Exception: {}.".format(e))
        log.error("Product could not be updated. Error code: {}. Error message: {}".format(e.response['Error']['Code'], e.response['Error']['Message']))

        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise Exception('Product did not exist.')
        else:
            raise Exception('Unexpected error when updating product.')

    log.info("Add response: {}".format(response))

    if 'quantity' in response['Attributes']:
        quantity = int(response['Attributes']['quantity']['N'])
    else:
        raise Exception('No updates to quantity were required.')

    return quantity
