import json
import os
import boto3
from lists import common, logger

log = logger.setup_logger()


def handler(event, context):
    response = update_list_main(event)
    return response


def update_list_main(event):
    try:
        table_name = common.get_env_variable(os.environ, 'TABLE_NAME')
        identity = common.get_identity(event, os.environ)
        list_id = common.get_path_parameter(event, 'id')
        attribute_details = get_attribute_details(event)
        common.confirm_owner(table_name, identity, list_id)

        items = get_items_to_update(table_name, list_id)
        updated_attributes = update_list(table_name, items, attribute_details)
    except Exception as e:
        response = common.create_response(500, json.dumps({'error': str(e)}))
        return response

    response = common.create_response(200, json.dumps(updated_attributes))
    return response


def get_attribute_details(event):
    if event['body'] == "null":
        raise Exception('API Event Body was empty.')

    try:
        body = event['body']
        log.info("Event body: " + json.dumps(body))
    except Exception:
        log.error("API Event was empty.")
        raise Exception('API Event was empty.')

    try:
        update_attributes = json.loads(body)
    except Exception:
        log.error("API Event did not contain a valid body.")
        raise Exception('API Event did not contain a valid body.')

    expected_keys = ["title", "description", "eventDate", "occasion", "imageUrl"]

    if list(update_attributes.keys()) != expected_keys:
        log.error("Event body did not contain the expected keys " + str(expected_keys) + ".")
        raise Exception("Event body did not contain the expected keys " + str(expected_keys) + ".")

    return update_attributes


def get_items_to_update(table_name, list_id):
    dynamodb = boto3.client('dynamodb')
    log.info("Querying table {} to find all items associated with list id {}".format(table_name, list_id))

    try:
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="PK = :PK",
            ExpressionAttributeValues={":PK":  {'S': "LIST#{}".format(list_id)}}
        )
        log.info("All items in query response. ({})".format(response['Items']))
    except Exception as e:
        log.info("Exception: " + str(e))
        raise Exception("Unexpected error when getting lists from table.")

    if len(response['Items']) == 0:
        log.info("No items for the list {} were found.".format(list_id))
        raise Exception("No list exists with this ID.")

    items = []
    for item in response['Items']:
        if item['SK']['S'].startswith("USER") or item['SK']['S'].startswith("SHARE") or item['SK']['S'].startswith("PENDING"):
            log.info("Adding item to list of items to update: {}".format(item))
            items.append(item)

    return items


def update_list(table_name, items, new_attribute_values):
    dynamodb = boto3.client('dynamodb')
    update_results = []
    for item in items:
        log.info("Updating item with PK ({}), SK ({}) with attribute values: {}".format(item['PK']['S'], item['SK']['S'], json.dumps(new_attribute_values)))

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
            log.info("update item exception: " + str(e))
            raise Exception("Unexpected error when updating the list item.")

        log.info("Attributes updated: " + json.dumps(response['Attributes']))

        updates = {}
        for attribute in response['Attributes']:
            updates[attribute] = response['Attributes'][attribute]['S']

        update_results.append({
            'PK': item['PK']['S'],
            'SK': item['SK']['S'],
            'updates': updates
        })

    return update_results
