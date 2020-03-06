import json
import os
import boto3
from lists import common, common_table_ops, logger

log = logger.setup_logger()

dynamodb = boto3.client('dynamodb')

ses = boto3.client('ses', region_name='eu-west-1')
SENDER = "Ewelists <contact@ewelists.com>"


def handler(event, context):
    response = purchase_main(event)
    return response


def purchase_main(event):
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

        # Get user
        user = common.get_user(event, os.environ, table_name, index_name)

        # Get reservation to know how what the quantity reserved was. As well as the reservation id
        reserved_item = common_table_ops.get_reserved_details_item(table_name, list_id, product_id, user['id'])

        # Check that not already purchased
        common.gift_is_reserved(reserved_item)

        # Get product to ensure we know the latest quantities.
        product_item = common_table_ops.get_product_item(table_name, list_id, product_id)

        # Calculate reserved and purchased quantities
        product_reserved_q = new_reserved_quantity(product_item['reserved'], reserved_item['quantity'])
        product_purchased_q = new_purchased_quantity(product_item['purchased'], reserved_item['quantity'])

        # update table with transaction
        product_key = common.create_product_key(list_id, product_id)
        reserved_key = common.create_reserved_key(list_id, product_id, user)
        reservation_key = common.create_reservation_key(reserved_item['reservationId'])
        update_product_reserved_and_reservation_items(table_name, product_key, product_reserved_q, product_purchased_q, reserved_key, reservation_key)

        # Send confirmation
        data = create_email_data(domain_name, user['name'], list_id, list_title, request_reserve_quantity, product)
        common.send_email(user['email'], template, data)

    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    data = {'purchased': True}
    response = common.create_response(200, json.dumps(data))
    return response


def new_reserved_quantity(product_reserved_quantity, user_reserved_quantity):
    new_quantity = product_reserved_quantity - user_reserved_quantity
    log.info("Product reserved quantity updating from {} to {}".format(product_reserved_quantity, new_quantity))

    return new_quantity


def new_purchased_quantity(product_purchased_quantity, user_reserved_quantity):
    new_quantity = product_purchased_quantity + user_reserved_quantity
    log.info("Product purchased quantity updating from {} to {}".format(product_purchased_quantity, new_quantity))

    return new_quantity


def update_product_reserved_and_reservation_items(table_name, product_key, product_reserved_q, product_purchased_q, reserved_key, reservation_key):
    try:
        response = dynamodb.transact_write_items(
            TransactItems=[
                {
                    'Update': {
                        'TableName': table_name,
                        'Key': product_key,
                        'UpdateExpression': "set reserved = :r, purchased = :p",
                        'ExpressionAttributeValues': {
                            ':r': {'N': str(product_reserved_q)},
                            ':p': {'N': str(product_purchased_q)}
                        }
                    }
                },
                {
                    'Update': {
                        'TableName': table_name,
                        'Key': reserved_key,
                        'UpdateExpression': "set #st = :s",
                        'ExpressionAttributeValues': {
                            ':s': {'S': 'purchased'},
                        },
                        'ExpressionAttributeNames': {
                            '#st': 'state'
                        }
                    }
                },
                {
                    'Update': {
                        'TableName': table_name,
                        'Key': reservation_key,
                        'UpdateExpression': "set #st = :s",
                        'ExpressionAttributeValues': {
                            ':s': {'S': 'purchased'},
                        },
                        'ExpressionAttributeNames': {
                            '#st': 'state'
                        }
                    }
                }
            ]
        )

        log.info("Attributes updated: " + json.dumps(response))
    except Exception as e:
        log.info("Transaction write exception: " + str(e))
        raise Exception("Unexpected error when confirming purchase of product.")

    return True


def create_email_data(domain_name, name, list_id, title, quantity, product):
    template_data = {
        "name": name,
        "list_title": title,
        "list_url": domain_name + "/lists/" + list_id,
        "quantity": quantity,
        "brand": product['brand'],
        "details": product['details'],
        "product_url": product['productUrl'],
        "image_url": product['imageUrl']
    }

    return template_data
