import json
import os
import boto3
from lists import common, logger

log = logger.setup_logger()


def handler(event, context):
    response = delete_product_main(event)
    return response


def delete_product_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common.get_identity(event, os.environ)
        list_id = common.get_path_parameter(event, 'id')
        product_id = common.get_path_parameter(event, 'productid')
        common.confirm_owner(table_name, identity, list_id)

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
    dynamodb = boto3.client('dynamodb')
    
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
