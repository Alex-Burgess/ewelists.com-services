import json
import os
import boto3
from lists import common, common_table_ops, common_kpi, logger

log = logger.setup_logger()

SENDER = "Ewelists <contact@ewelists.com>"


def handler(event, context):
    log.info("Path Parameters: {}".format(json.dumps(event['pathParameters'])))
    log.info("Body attributes: {}".format(json.dumps(event['body'])))
    response = purchase_main(event)
    return response


def purchase_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        resv_id_index = common.get_env_variable(os.environ, 'RESERVATIONID_INDEX')
        confirm_template = common.get_env_variable(os.environ, 'CONFIRM_TEMPLATE_NAME')
        update_template = common.get_env_variable(os.environ, 'UPDATE_TEMPLATE_NAME')
        domain_name = common.get_env_variable(os.environ, 'DOMAIN_NAME')

        resv_id = common.get_path_parameter(event, 'reservationid')
        email = common.get_path_parameter(event, 'email')
        product = common.get_body_attribute(event, 'product')

        # Get reservation to know how what the quantity reserved was. As well as the reservation id
        reservation = common_table_ops.get_reservation(table_name, resv_id_index, resv_id)
        common.confirm_reservation_owner(reservation, email)
        common.gift_is_reserved(reservation)

        # Get list owner details
        list_owner = common_table_ops.get_users_details(table_name, reservation['listOwnerId'])

        # Get product to ensure we know the latest quantities.
        product_item = common_table_ops.get_product_item(table_name, reservation['listId'], reservation['productId'])

        # Calculate reserved and purchased quantities
        product_reserved_q = new_reserved_quantity(product_item['reserved'], reservation['quantity'])
        product_purchased_q = new_purchased_quantity(product_item['purchased'], reservation['quantity'])

        # update table with transaction
        product_key = common.create_product_key(reservation['listId'], reservation['productId'])
        reservation_key = common.create_reservation_key(reservation)
        update_product_and_reservation(table_name, product_key, product_reserved_q, product_purchased_q, reservation_key)

        # Send confirmation
        data = create_confirm_email_data(domain_name, reservation['name'], reservation['listId'], reservation['listTitle'], reservation['quantity'], product)
        common.send_email(reservation['email'], confirm_template, data)

        # Send update to list owner
        update_data = create_update_email_data(domain_name, list_owner['name'], reservation['listId'], reservation['listTitle'], reservation['quantity'], reservation['name'], product)
        common.send_email(list_owner['email'], update_template, update_data)

    except Exception as e:
        log.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        log.info("Returning response: {}".format(response))
        return response

    common_kpi.post(os.environ, event, 'Purchased')

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


def update_product_and_reservation(table_name, product_key, product_reserved_q, product_purchased_q, reservation_key):
    dynamodb = boto3.client('dynamodb')

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


def create_confirm_email_data(domain_name, name, list_id, title, quantity, product):
    imageUrl = common.check_image_url(product['imageUrl'])

    template_data = {
        "name": name,
        "list_title": title,
        "list_url": domain_name + "/lists/" + list_id,
        "quantity": quantity,
        "brand": product['brand'],
        "details": product['details'],
        "product_url": product['productUrl'],
        "image_url": imageUrl
    }

    return template_data


def create_update_email_data(domain_name, name, list_id, title, quantity, reserved_name, product):
    imageUrl = common.check_image_url(product['imageUrl'])

    template_data = {
        "name": name,
        "list_title": title,
        "list_url": domain_name + "/edit/" + list_id + "?tab=2",
        "quantity": quantity,
        "reserved_name": reserved_name,
        "brand": product['brand'],
        "details": product['details'],
        "product_url": product['productUrl'],
        "image_url": imageUrl
    }

    return template_data
