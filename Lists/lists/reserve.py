import json
import os
import time
import uuid
import boto3
from lists import common, common_table_ops, common_kpi, logger

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
        product_key = common.create_product_key(list_id, product_id)
        list_details = common.get_list_details(table_name, list_id)
        reservation_item = create_reservation_item(list_id, list_details['listOwner'], list_title, product_id, product['type'], resv_id, user, request_reserve_quantity)
        create_reservation(table_name, new_product_reserved_quantity, product_key, reservation_item)

        # Step 5 - Send reserve confirmation email
        data = create_email_data(domain_name, user['name'], resv_id, list_id, list_title, request_reserve_quantity, product)
        common.send_email(user['email'], template, data)

    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    common_kpi.post(os.environ, event, 'Reserved')
    data = {'reservation_id': resv_id}
    response = common.create_response(200, json.dumps(data))
    return response


def create_reservation_item(list_id, list_owner_id, list_title, product_id, product_type, resv_id, user, request_reserve_quantity):
    return {
        'PK': {'S': "LIST#{}".format(list_id)},
        'SK': {'S': "RESERVATION#{}#{}#{}".format(product_id, user['id'], resv_id)},
        'reservationId': {'S': resv_id},
        'productId': {'S': product_id},
        'userId': {'S': user['id']},
        'listId': {'S': list_id},
        'listOwnerId': {'S': list_owner_id},
        'name': {'S': user['name']},
        'email': {'S': user['email']},
        'quantity': {'N': str(request_reserve_quantity)},
        'state': {'S': 'reserved'},
        'reservedAt': {'N': str(int(time.time()))},
        'listTitle': {'S': list_title},
        'productType': {'S': product_type}
    }


def create_reservation(table_name, new_product_reserved_quantity, product_key, reservation_item):
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
    imageUrl = common.check_image_url(product['imageUrl'])

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
        "image_url": imageUrl
    }

    return template_data
