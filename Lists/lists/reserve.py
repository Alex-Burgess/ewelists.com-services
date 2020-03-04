import json
import os
import time
import uuid
import boto3
from botocore.exceptions import ClientError
from lists import common, common_table_ops, logger

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')

ses = boto3.client('ses', region_name='eu-west-1')
SENDER = "Ewelists <contact@ewelists.com>"


def handler(event, context):
    response = reserve_main(event)
    return response


def reserve_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        index_name = common.get_env_variable(os.environ, 'INDEX_NAME')
        template = common.get_env_variable(os.environ, 'TEMPLATE_NAME')
        domain_name = common.get_env_variable(os.environ, 'DOMAIN_NAME')
        list_id = common.get_path_parameter(event, 'id')
        list_title = common.get_body_attribute(event, 'title')
        product_id = common.get_path_parameter(event, 'productid')
        product = common.get_body_attribute(event, 'product')
        request_reserve_quantity = common.get_body_attribute(event, 'quantity')

        # Step 1 - check if reserved item exists
        user = common.get_user(event, os.environ, table_name, index_name)
        common_table_ops.check_product_not_reserved_by_user(table_name, list_id, product_id, user['id'])

        # Step 2 - get product item.
        product_item = common_table_ops.get_product_item(table_name, list_id, product_id)

        # Step 3 - Calculate new reserved quantity of product.
        new_product_reserved_quantity = common.calculate_new_reserved_quantity(product_item, request_reserve_quantity)

        # Step 4 - Update, in one transaction, the product reserved quantity and create reserved item.
        resv_id = str(uuid.uuid4())
        product_key = create_product_key(list_id, product_id)
        reserved_item = create_reserved_item(list_id, product_id, resv_id, user, request_reserve_quantity)
        reservation_item = create_reservation_item(list_id, list_title, product_id, product['type'], resv_id, user, request_reserve_quantity)
        create_reservation(table_name, resv_id, new_product_reserved_quantity, product_key, reserved_item, reservation_item)

        # Step 5 - Send reserve confirmation email
        data = create_email_data(domain_name, user['name'], resv_id, list_id, list_title, request_reserve_quantity, product)
        send_email(user['email'], template, data)

    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    data = {'reservation_id': resv_id}
    response = common.create_response(200, json.dumps(data))
    return response


def create_product_key(list_id, product_id):
    return {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "PRODUCT#{}".format(product_id)}
    }


def create_reserved_item(list_id, product_id, resv_id, user, request_reserve_quantity):
    return {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "RESERVED#{}#{}".format(product_id, user['id'])},
        'name': {'S': user['name']},
        'productId': {'S': product_id},
        'userId': {'S': user['id']},
        'quantity': {'N': str(request_reserve_quantity)},
        'reservedAt': {'N': str(int(time.time()))},
        'reservationId': {'S': resv_id},
        'state': {'S': 'reserved'}
    }


def create_reservation_item(list_id, list_title, product_id, product_type, resv_id, user, request_reserve_quantity):
    return {
        'PK': {'S': "RESERVATION#{}".format(resv_id)},
        'SK': {'S': "RESERVATION#{}".format(resv_id)},
        'reservationId': {'S': resv_id},
        'userId': {'S': user['id']},
        'email': {'S': user['email']},
        'name': {'S': user['name']},
        'listId': {'S': list_id},
        'title': {'S': list_title},
        'productId': {'S': product_id},
        'productType': {'S': product_type},
        'quantity': {'N': str(request_reserve_quantity)},
        'state': {'S': 'reserved'}
    }


def create_reservation(table_name, resv_id, new_product_reserved_quantity, product_key, reserved_item, reservation_item):
    try:
        response = dynamodb.transact_write_items(
            TransactItems=[
                {
                    'Update': {
                        'TableName': table_name,
                        'Key': product_key,
                        'UpdateExpression': "set reserved = :r",
                        'ExpressionAttributeValues': {
                            ':r': {'N': str(new_product_reserved_quantity)},
                        }
                    }
                },
                {
                    'Put': {
                        'TableName': table_name,
                        'Item': reserved_item
                    }
                },
                {
                    'Put': {
                        'TableName': table_name,
                        'Item': reservation_item
                    }
                }
            ]
        )

        log.info("Attributes updated: " + json.dumps(response))
    except Exception as e:
        log.info("Transaction write exception: " + str(e))
        raise Exception("Unexpected error when reserving product.")

    return True


def create_email_data(domain_name, name, resv_id, list_id, title, quantity, product):
    template_data = {
        "name": name,
        "list_title": title,
        "list_url": domain_name + "/lists/" + list_id,
        "quantity": quantity,
        "confirm_url": domain_name + "/reserve/" + resv_id,
        "edit_url": domain_name + "/reserve/" + resv_id,
        "brand": product['brand'],
        "details": product['details'],
        "product_url": product['productUrl'],
        "image_url": product['imageUrl']
    }

    return template_data


def send_email(email, template, template_data):
    try:
        response = ses.send_templated_email(
            Source=SENDER,
            Destination={
                'ToAddresses': [email],
            },
            ReplyToAddresses=[SENDER],
            Template=template,
            TemplateData=json.dumps(template_data)
        )
    except ClientError as e:
        raise Exception("Could not send reserve email: " + e.response['Error']['Message'])
    else:
        log.info("Email sent! Message ID: " + response['MessageId'])

    return True
