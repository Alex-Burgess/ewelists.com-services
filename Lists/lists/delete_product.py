import json
import os
import boto3
from lists import common, common_table_ops, logger

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = delete_product_main(event)
    return response


def delete_product_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common.get_identity(event, os.environ)
        list_id = common.get_path_parameter(event, 'id')
        product_id = common.get_path_parameter(event, 'productid')

        list_item = common_table_ops.get_list(table_name, identity, list_id)
        common.confirm_owner(identity, list_id, [list_item])

        message = delete_product_item(table_name, list_id, product_id)
    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    data = {'message': message}
    response = common.create_response(200, json.dumps(data))
    return response


def delete_product_item(table_name, list_id, product_id):
    key = {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    condition = {
        ':PK': {'S': "LIST#{}".format(list_id)},
        ':SK': {'S': "PRODUCT#{}".format(product_id)}
    }

    try:
        log.info("Deleting product item: {}".format(key))
        response = dynamodb.delete_item(
            TableName=table_name,
            Key=key,
            ConditionExpression="PK = :PK AND SK = :SK",
            ExpressionAttributeValues=condition
        )
    except Exception as e:
        log.error("Product could not be deleted: {}".format(e))
        raise Exception('Product could not be deleted.')

    log.info("Delete response: {}".format(response))

    return True
