import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import get_list

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_get_list_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists/{id}",
        "path": "/lists/12345678-abcd-abcd-123456789112",
        "httpMethod": "GET",
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
            "id": "12345678-abcd-abcd-123456789112"
        },
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/lists/{id}",
            "httpMethod": "GET",
            "extendedRequestId": "BQGojGkBjoEFsTw=",
            "requestTime": "08/Oct/2019:16:22:40 +0000",
            "path": "/test/lists/12345678-abcd-abcd-123456789112",
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
                "cognitoAuthenticationProvider": "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:42cf26f5-407c-47cf-bcb6-f70cd63ac119",
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

    items = [
        {"PK": "USER#42cf26f5-407c-47cf-bcb6-f70cd63ac119", "SK": "USER#42cf26f5-407c-47cf-bcb6-f70cd63ac119", "email": "test.user@gmail.com", "name": "Test User", "userId": "42cf26f5-407c-47cf-bcb6-f70cd63ac119"},
        {"PK": "USER#db9476fd-de77-4977-839f-4f943ff5d684", "SK": "USER#db9476fd-de77-4977-839f-4f943ff5d684", "email": "test.user2@gmail.com", "name": "Test User2", "userId": "db9476fd-de77-4977-839f-4f943ff5d684"},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "USER#42cf26f5-407c-47cf-bcb6-f70cd63ac119", "userId": "42cf26f5-407c-47cf-bcb6-f70cd63ac119", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-abcd-abcd-123456789112", "createdAt": "2018-09-01T10:00:00", "listOwner": "42cf26f5-407c-47cf-bcb6-f70cd63ac119", "description": "A gift list for Api Childs birthday.", "eventDate": "2019-09-01"},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "SHARE#42cf26f5-407c-47cf-bcb6-f70cd63ac119", "userId": "42cf26f5-407c-47cf-bcb6-f70cd63ac119", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-abcd-abcd-123456789112", "createdAt": "2018-09-01T10:00:00", "listOwner": "42cf26f5-407c-47cf-bcb6-f70cd63ac119", "description": "A gift list for Api Childs birthday.", "eventDate": "2019-09-01"},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "SHARE#db9476fd-de77-4977-839f-4f943ff5d684", "userId": "db9476fd-de77-4977-839f-4f943ff5d684", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-abcd-abcd-123456789112", "createdAt": "2018-09-01T10:00:00", "listOwner": "42cf26f5-407c-47cf-bcb6-f70cd63ac119", "description": "A gift list for Api Childs birthday.", "eventDate": "2019-09-01"},
        {"PK": "LIST#49d47a66-8825-4872-85c2-e15a12d19aed", "SK": "USER#42cf26f5-407c-47cf-bcb6-f70cd63ac119", "userId": "42cf26f5-407c-47cf-bcb6-f70cd63ac119", "title": "Oscar's 2019 Christmas List", "occasion": "Christmas", "listId": "49d47a66-8825-4872-85c2-e15a12d19aed", "listOwner": "1234250a-0fb0-4b32-9842-041c69be1234", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "eventDate": "2019-12-25"},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "PRODUCT#1000", "quantity": 1, "reserved": 0},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "PRODUCT#1001", "quantity": 2, "reserved": 0},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "PRODUCT#1002", "quantity": 2, "reserved": 1}
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetListQuery:
    def test_get_list_query(self, dynamodb_mock):
        cognito_user_id = "42cf26f5-407c-47cf-bcb6-f70cd63ac119"
        items = get_list.get_list_query('lists-unittest', cognito_user_id, "12345678-abcd-abcd-123456789112")
        assert len(items) == 6, "Number of items deleted was not as expected."

    def test_get_list_query_no_table_name(self, dynamodb_mock):
        cognito_user_id = "42cf26f5-407c-47cf-bcb6-f70cd63ac119"

        with pytest.raises(Exception) as e:
            get_list.get_list_query('lists-unittes', cognito_user_id, "12345678-abcd-abcd-123456789112")
        assert str(e.value) == "Unexpected error when getting list item from table.", "Exception not as expected."

    def test_get_list_query_for_item_that_does_not_exist(self, dynamodb_mock):
        cognito_user_id = "42cf26f5-407c-47cf-bcb6-f70cd63ac119"

        with pytest.raises(Exception) as e:
            get_list.get_list_query('lists-unittest', cognito_user_id, "12345678-abcd-abcd-123456789112-diff")
        assert str(e.value) == "No query results for List ID 12345678-abcd-abcd-123456789112-diff and user: 42cf26f5-407c-47cf-bcb6-f70cd63ac119.", "Exception not as expected."


class TestGetListMain:
    def test_get_list_main(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-abcd-abcd-123456789112", "Get list response did not contain a listId."
        assert body['list']['title'] == "Api Child's 1st Birthday", "Get list response did not contain a title."
        assert body['list']['description'] == "A gift list for Api Childs birthday.", "Get list response did not contain a description."
        assert body['list']['occasion'] == "Birthday", "Get list response did not contain an occasion."
        assert len(body['products']) == 3, "Get list response did not contain correct number of products."
        assert body['products'][0]['productId'] == "1000", "Product ID was not correct."
        assert body['products'][0]['quantity'] == 1, "Quantity of product was not correct."
        assert body['products'][0]['reserved'] == 0, "Reserved quantity of product was not correct."

        assert body['products'][1]['productId'] == "1001", "Product ID was not correct."
        assert body['products'][1]['quantity'] == 2, "Quantity of product was not correct."
        assert body['products'][1]['reserved'] == 0, "Reserved quantity of product was not correct."

        assert body['products'][2]['productId'] == "1002", "Product ID was not correct."
        assert body['products'][2]['quantity'] == 2, "Quantity of product was not correct."
        assert body['products'][2]['reserved'] == 1, "Reserved quantity of product was not correct."

    def test_get_list_main_no_table(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting list item from table.', "Get list response did not contain the correct error message."

    def test_get_list_that_requestor_does_not_own(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_get_list_event['pathParameters']['id'] = "49d47a66-8825-4872-85c2-e15a12d19aed"

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == "Owner of List ID 49d47a66-8825-4872-85c2-e15a12d19aed did not match user id of requestor: 42cf26f5-407c-47cf-bcb6-f70cd63ac119.", "Get list response did not contain the correct error message."


def test_handler(api_gateway_get_list_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = get_list.handler(api_gateway_get_list_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"list": .*}', response['body'])
