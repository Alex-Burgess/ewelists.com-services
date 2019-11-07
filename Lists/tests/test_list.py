import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import list

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_listall_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists",
        "path": "/lists",
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
        "pathParameters": "null",
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/lists",
            "httpMethod": "GET",
            "extendedRequestId": "BQGojGkBjoEFsTw=",
            "requestTime": "08/Oct/2019:16:22:40 +0000",
            "path": "/test/lists",
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
                },
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'userId-index',
                    'KeySchema': [
                         {
                             'AttributeName': 'userId',
                             'KeyType': 'HASH'
                         },
                         {
                             'AttributeName': 'PK',
                             'KeyType': 'RANGE'
                         }
                     ],
                     'Projection': {
                        'ProjectionType': 'ALL'
                     }
                }
            ]
        )

    # 3 users. User 1, owns list 1, which is not shared.  user 2, owns list 2 and 3 which are shared with user 1.  User 3 has no lists.
    items = [
        {"PK": "USER#12345678-user-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "email": "test.user@gmail.com", "name": "Test User", "userId": "12345678-user-0001-1234-abcdefghijkl"},
        {"PK": "USER#12345678-user-0002-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "email": "test.user2@gmail.com", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl"},
        {"PK": "USER#12345678-user-0003-1234-abcdefghijkl", "SK": "USER#12345678-user-0003-1234-abcdefghijkl", "email": "test.user3@gmail.com", "name": "Test User3", "userId": "12345678-user-0003-1234-abcdefghijkl"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0002-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars birthday.", "eventDate": "31 October 2018"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0002-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars birthday.", "eventDate": "31 October 2018"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0002-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars birthday.", "eventDate": "31 October 2018"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 2nd Birthday", "occasion": "Birthday", "listId": "12345678-list-0003-1234-abcdefghijkl", "createdAt": "2019-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars 2nd Birthday.", "eventDate": "31 October 2019"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 2nd Birthday", "occasion": "Birthday", "listId": "12345678-list-0003-1234-abcdefghijkl", "createdAt": "2019-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars 2nd Birthday.", "eventDate": "31 October 2019"},
        {"PK": "LIST#12345678-list-0003-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's 2nd Birthday", "occasion": "Birthday", "listId": "12345678-list-0003-1234-abcdefghijkl", "createdAt": "2019-09-01T10:00:00", "listOwner": "12345678-user-0002-1234-abcdefghijkl", "description": "A gift list for Oscars 2nd Birthday.", "eventDate": "31 October 2019"}
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetLists:
    def test_get_lists_for_requestor(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        lists_response = list.get_lists('lists-unittest', 'userId-index', user_id)

        test_user = {"email": "test.user@gmail.com"}
        assert lists_response['user'] == test_user, "Test user was not as expected."

        owned_list = {"listId": "12345678-list-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019"}
        assert len(lists_response['owned']) == 1, "User should only own 1 list."
        assert lists_response['owned'][0] == owned_list, "Details of the list owned by user was not as expected."

        shared_list1 = {"listId": "12345678-list-0002-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "description": "A gift list for Oscars birthday.", "eventDate": "31 October 2018"}
        shared_list2 = {"listId": "12345678-list-0003-1234-abcdefghijkl", "title": "Oscar's 2nd Birthday", "occasion": "Birthday", "description": "A gift list for Oscars 2nd Birthday.", "eventDate": "31 October 2019"}
        assert len(lists_response['shared']) == 2, "User should only have 2 lists shared with them."
        assert lists_response['shared'][0] == shared_list1, "Details of the list shared with user was not as expected."
        assert lists_response['shared'][1] == shared_list2, "Details of the list shared with user was not as expected."

    def test_get_lists_bad_table_name(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            list.get_lists('lists-unittes', 'userId-index', user_id)
        assert str(e.value) == "Unexpected error when getting lists from table.", "Exception not as expected."

    def test_get_lists_bad_index_name(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            list.get_lists('lists-unittest', 'userId-inde', user_id)
        assert str(e.value) == "Unexpected error when getting lists from table.", "Exception not as expected."

    def test_get_lists_for_user_with_no_lists(self, dynamodb_mock):
        user_id = '12345678-user-0003-1234-abcdefghijkl'
        lists_response = list.get_lists('lists-unittest', 'userId-index', user_id)
        assert len(lists_response['owned']) == 0, "Number of lists was not 0."
        assert len(lists_response['shared']) == 0, "Number of lists was not 0."


class TestListMain:
    def test_list_main(self, api_gateway_listall_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'userId-index')
        response = list.list_main(api_gateway_listall_event)
        body = json.loads(response['body'])

        assert len(body['owned']) == 1, "Number of lists returned was not as expected."
        assert len(body['shared']) == 2, "Number of lists returned was not as expected."

    def test_list_main_no_table(self, api_gateway_listall_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'userId-index')
        response = list.list_main(api_gateway_listall_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting lists from table.', "Exception was not as expected."

    def test_list_main_user_with_no_lists(self, api_gateway_listall_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'userId-index')
        api_gateway_listall_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"
        response = list.list_main(api_gateway_listall_event)
        body = json.loads(response['body'])

        assert len(body['owned']) == 0, "Number of lists returned was not as expected."
        assert len(body['shared']) == 0, "Number of lists returned was not as expected."


def test_handler(api_gateway_listall_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'INDEX_NAME', 'userId-index')
    response = list.handler(api_gateway_listall_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"user": .*}', response['body'])
