import json

import boto3

table_name = 'lists-test'
file_name = 'items.json'

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)

items = []

try:
    with open(file_name, 'r') as f:
        for row in f:
            items.append(json.loads(row))

    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)

    print("Adding items to table [{}]".format(table_name))
except Exception as e:
    print("Could not connect to table. Error:")
    print(e)
