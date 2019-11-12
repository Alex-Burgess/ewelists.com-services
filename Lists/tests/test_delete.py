import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import delete

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_delete_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists/{id}",
        "path": "/lists/12345678-list-0001-1234-abcdefghijkl",
        "httpMethod": "DELETE",
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "GB",
            "Content-Type": "text/plain",
            "Host": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "Postman-Token": "512388b6-c036-4d11-a6c9-adf8e07e1da0",
            "User-Agent": "PostmanRuntime/7.15.2",
            "Via": "1.1 a1cb6e97bccd4899987b343ae5d4c252.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "zJgUVrLX5O4d-B43SVe4Bs6YVpSTWXxrAVtWjeF0FcAnXJ8dARKQRA==",
            "x-amz-content-sha256": "b9d4c66e0ae3c09af8a6ce4c99518f244c3db701a196021c79f094b51e9b49d4",
            "x-amz-date": "20191008T162240Z",
            "X-Amzn-Trace-Id": "Root=1-5d9cb7d0-6965798907570a0728570212",
            "X-Forwarded-For": "5.81.150.55, 70.132.38.104",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "queryStringParameters": "null",
        "multiValueQueryStringParameters": "null",
        "pathParameters": {
            "id": "12345678-list-0001-1234-abcdefghijkl"
        },
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/lists/{id}",
            "httpMethod": "DELETE",
            "extendedRequestId": "BQGojGkBjoEFsTw=",
            "requestTime": "08/Oct/2019:16:22:40 +0000",
            "path": "/test/lists/12345678-list-0001-1234-abcdefghijkl",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "test",
            "domainPrefix": "4sdcvv0n2e",
            "requestTimeEpoch": 1570551760227,
            "requestId": "a3d965cd-a79b-4249-867a-a03eb858a839",
            "identity": {
                "cognitoIdentityPoolId": "eu-west-1:2208d797-dfc9-40b4-8029-827c9e76e029",
                "accountId": "123456789012",
                "cognitoIdentityId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c",
                "caller": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials",
                "sourceIp": "31.49.230.217",
                "principalOrgId": "o-d8jj6dyqv2",
                "accessKey": "ABCDEFGPDMJL4EB35H6H",
                "cognitoAuthenticationType": "authenticated",
                "cognitoAuthenticationProvider": "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0001-1234-abcdefghijkl",
                "userArn": "arn:aws:sts::123456789012:assumed-role/Ewelists-test-CognitoAuthRole/CognitoIdentityCredentials",
                "userAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Mobile Safari/537.36",
                "user": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials"
            },
            "domainName": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "apiId": "4sdcvv0n2e"
        },
        "body": "null",
        "isBase64Encoded": "false"
    }


@pytest.fixture
def dynamodb_mock():
    table_name = 'lists-unittest'

    mock = mock_dynamodb2()
    mock.start()

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'PK',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'SK',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'SK',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

    # 2 Users, 1 List with 3 products and shared with owner and 1 other user.
    items = [
        {"PK": "USER#12345678-user-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "email": "test.user@gmail.com", "name": "Test User", "userId": "12345678-user-0001-1234-abcdefghijkl"},
        {"PK": "USER#12345678-user-0002-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "email": "test.user2@gmail.com", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1000", "quantity": 1, "reserved": 0},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1001", "quantity": 2, "reserved": 0},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1002", "quantity": 2, "reserved": 1}
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestDeleteItems:
    def test_delete_list_item(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        items = [
            {"PK": {'S': "LIST#{}".format(list_id)}, 'SK': {'S': "USER#{}".format(list_id)}},
        ]

        message = delete.delete_items('lists-unittest', user_id, list_id, items)
        assert message == 'Deleted all items [1] for List ID: 12345678-list-0001-1234-abcdefghijkl and user: 12345678-user-0001-1234-abcdefghijkl.', "Delete message was not as expected."

    def test_delete_product_item(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        items = [
            {"PK": {'S': "LIST#{}".format(list_id)}, 'SK': {'S': "PRODUCT#1000"}, "quantity": 1, "reserved": 0}
        ]

        message = delete.delete_items('lists-unittest', user_id, list_id, items)
        assert message == 'Deleted all items [1] for List ID: 12345678-list-0001-1234-abcdefghijkl and user: 12345678-user-0001-1234-abcdefghijkl.', "Delete message was not as expected."

    def test_delete_multiple_list_items(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        item_keys = [
            {"PK": {'S': "LIST#{}".format(list_id)}, 'SK': {'S': "USER#{}".format(list_id)}},
            {"PK": {'S': "LIST#{}".format(list_id)}, 'SK': {'S': "SHARED#{}".format(list_id)}}
        ]

        message = delete.delete_items('lists-unittest', user_id, list_id, item_keys)
        assert message == 'Deleted all items [2] for List ID: 12345678-list-0001-1234-abcdefghijkl and user: 12345678-user-0001-1234-abcdefghijkl.', "Delete message was not as expected."

    @pytest.mark.skip(reason="Moto is not throwing an exception when deleting with ConditionExpression")
    def test_delete_item_no_list(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0009-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete.delete_item('lists-unittest', user_id, list_id)
        assert str(e.value) == "List does not exist.", "Exception not as expected."


class TestGetItemsAssociatedWithList:
    def test_get_items_associated_with_list(self, dynamodb_mock):
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        items = delete.get_items_associated_with_list('lists-unittest', list_id)
        assert len(items) == 6, "Number of items deleted was not as expected."


class TestDeleteMain:
    def test_delete_main(self, api_gateway_delete_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = delete.delete_main(api_gateway_delete_event)
        body = json.loads(response['body'])

        assert body['deleted'], "Delete main response did not contain the correct status."
        assert len(body['listId']) == 36, "Create main response did not contain a listId."
        assert body['message'] == 'Deleted all items [6] for List ID: 12345678-list-0001-1234-abcdefghijkl and user: 12345678-user-0001-1234-abcdefghijkl.', "Delete main response did not contain the correct message."

    def test_delete_main_with_bad_table_name(self, api_gateway_delete_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = delete.delete_main(api_gateway_delete_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Unexpected error when getting lists from table.', "Create main response did not contain the correct error message."

    def test_delete_main_with_bad_user(self, api_gateway_delete_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_delete_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"
        response = delete.delete_main(api_gateway_delete_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Owner of List ID 12345678-list-0001-1234-abcdefghijkl did not match user id of requestor: 12345678-user-0003-1234-abcdefghijkl.', "Create main response did not contain the correct error message."

    def test_delete_main_with_bad_list(self, api_gateway_delete_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_delete_event['pathParameters']['id'] = "12345678-list-0003-1234-abcdefghijkl"

        response = delete.delete_main(api_gateway_delete_event)
        body = json.loads(response['body'])
        assert body['error'] == 'No list exists with this ID.', "Create main response did not contain the correct error message."


def test_handler(api_gateway_delete_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = delete.handler(api_gateway_delete_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    assert re.match('{"deleted": .*}', response['body']), "Response body was not as expected."

    body = json.loads(response['body'])
    assert body['count'] == 6, "Number of items deleted was not as expected."
