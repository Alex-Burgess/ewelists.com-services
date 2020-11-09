import json
import os
import boto3
from lists import common, logger
from botocore.exceptions import ClientError

log = logger.setup_logger()


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
        notes = common.get_body_attribute_if_exists(event, 'notes')
        common.confirm_owner(table_name, identity, list_id)

        updates = update_product_item(table_name, list_id, product_id, quantity, notes)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(updates))
    return response


def update_expression(quantity, notes):
    expression = "set quantity = :q"

    if notes:
        expression = expression + ", notes = :n"

    return expression


def expression_attribute_values(quantity, notes):
    values = {
        ':q': {'N': str(quantity)}
    }

    if notes:
        values[':n'] = {'S': notes}

    return values


def update_product_item(table_name, list_id, product_id, quantity, notes):
    dynamodb = boto3.client('dynamodb')

    key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    try:
        log.info("Updating quantity of product item ({}) to {}".format(key, quantity))
        response = dynamodb.update_item(
            TableName=table_name,
            Key=key,
            UpdateExpression=update_expression(quantity, notes),
            ExpressionAttributeValues=expression_attribute_values(quantity, notes),
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

    updates = {}
    if 'quantity' in response['Attributes']:
        updates['quantity'] = int(response['Attributes']['quantity']['N'])

    if 'notes' in response['Attributes']:
        updates['notes'] = response['Attributes']['notes']['S']

    return updates
