import json
import os
import boto3
import logging
from lists import common

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = update_list_main(event)
    return response


def update_list_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        identity = common.get_identity(event, os.environ)
        list_id = common.get_list_id(event)
        attribute_details = get_attribute_details(event)
        items = get_items_to_update(table_name, list_id)
        common.confirm_owner(identity['userPoolSub'], list_id, items)
        updated_attributes = update_list(table_name, items, attribute_details)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    response = common.create_response(200, json.dumps(updated_attributes))
    return response


def get_attribute_details(event):
    if event['body'] == "null":
        raise Exception('API Event Body was empty.')

    try:
        body = event['body']
        logger.info("Event body: " + json.dumps(body))
    except Exception:
        logger.error("API Event was empty.")
        raise Exception('API Event was empty.')

    try:
        update_attributes = json.loads(body)
    except Exception:
        logger.error("API Event did not contain a valid body.")
        raise Exception('API Event did not contain a valid body.')

    expected_keys = ["title", "description", "eventDate", "occasion", "imageUrl"]

    if list(update_attributes.keys()) != expected_keys:
        logger.error("Event body did not contain the expected keys " + str(expected_keys) + ".")
        raise Exception("Event body did not contain the expected keys " + str(expected_keys) + ".")

    return update_attributes


def get_items_to_update(table_name, list_id):
    logger.info("Querying table {} to find all items associated with list id {}".format(table_name, list_id))

    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        logger.info("All items in query response. ({})".format(response['Items']))
    except Exception as e:
        logger.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting lists from table.")

    if len(response['Items']) == 0:
        logger.info("No items for the list {} were found.".format(list_id))
        raise Exception("No list exists with this ID.")

    items = []
    for item in response['Items']:
        if item['SK']['S'].startswith("USER") or item['SK']['S'].startswith("SHARE") or item['SK']['S'].startswith("PENDING"):
            logger.info("Adding item to list of items to update: {}".format(item))
            items.append(item)

    return items


def update_list(table_name, items, new_attribute_values):
    update_results = []
    for item in items:
        logger.info("Updating item with PK ({}), SK ({}) with attribute values: {}".format(item['PK']['S'], item['SK']['S'], json.dumps(new_attribute_values)))

        key = {
            'PK': {'S': item['PK']['S']},
            'SK': {'S': item['SK']['S']}
        }

        if new_attribute_values["eventDate"]:
            eventDate = new_attribute_values["eventDate"]
        else:
            eventDate = 'None'

        try:
            response = dynamodb.update_item(
                TableName=table_name,
                Key=key,
                UpdateExpression="set title = :t, description = :d, eventDate = :e, occasion = :o, imageUrl = :i",
                ExpressionAttributeValues={
                    ':t': {'S': new_attribute_values["title"]},
                    ':d': {'S': new_attribute_values["description"]},
                    ':e': {'S': eventDate},
                    ':o': {'S': new_attribute_values["occasion"]},
                    ':i': {'S': new_attribute_values["imageUrl"]}
                },
                ReturnValues="UPDATED_NEW"
            )

        except Exception as e:
            logger.info("update item exception: " + str(e))
            raise Exception("Unexpected error when updating the list item.")

        logger.info("Attributes updated: " + json.dumps(response['Attributes']))

        updates = {}
        for attribute in response['Attributes']:
            updates[attribute] = response['Attributes'][attribute]['S']

        update_results.append({
            'PK': item['PK']['S'],
            'SK': item['SK']['S'],
            'updates': updates
        })

    return update_results
