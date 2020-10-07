import json
import os
import boto3
import logging
from notfound import common
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


def handler(event, context):
    response = delete_main(event)
    return response


def delete_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        product_id = common.get_product_id(event)
        delete_product(table_name, identity, product_id)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'deleted': True}
    response = common.create_response(200, json.dumps(data))
    return response


def delete_product(table_name, cognito_user_id, product_id):
    dynamodb = boto3.client('dynamodb')
    
    logger.info("Deleting Product ID: {} for user: {}.".format(product_id, cognito_user_id))

    key = {
        'productId': {'S': product_id},
    }

    try:
        response = dynamodb.delete_item(
            TableName=table_name,
            Key=key,
            ConditionExpression="createdBy = :C",
            ExpressionAttributeValues={":C":  {'S': cognito_user_id}}
        )
        logger.info("Delete response: {}".format(response))
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            logger.info("Delete request failed for product_id: {} and user {} due to condition check on createdBy user id.".format(product_id, cognito_user_id))
            raise Exception("Product can not be deleted.")
        else:
            raise

    return True
