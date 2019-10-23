import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import get_shared_list

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
            "Host": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "Postman-Token": "68cd6f41-1d8a-420d-95ae-d46612ee8d54",
            "User-Agent": "PostmanRuntime/7.15.2",
            "Via": "1.1 5eade7e5ebbbd665bf0f8d23a84cc713.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "OgLVkBcert4ANwvUz3GBUX2aGDY_iiDv4QrQFFqha7v3y1gglIRm4g==",
            "x-amz-date": "20191007T153345Z",
            "X-Amzn-Trace-Id": "Root=1-5d9b5ad9-9cc41570632adb90a8ba3800",
            "X-Forwarded-For": "5.81.150.55, 70.132.15.85",
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
            "resourceId": "4j13uq",
            "resourcePath": "/lists/{id}",
            "httpMethod": "GET",
            "extendedRequestId": "BMsiDFARjoEFgOg=",
            "requestTime": "07/Oct/2019:15:33:45 +0000",
            "path": "/test/lists/12345678-abcd-abcd-123456789112",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "test",
            "domainPrefix": "4sdcvv0n2e",
            "requestTimeEpoch": 1570462425886,
            "requestId": "4fa38ad5-1706-4bdb-b0e2-6a5519cc12fa",
            "identity": {
                "cognitoIdentityPoolId": "eu-west-1:2208d797-dfc9-40b4-8029-827c9e76e029",
                "accountId": "123456789012",
                "cognitoIdentityId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684",
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
        {"PK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "SK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "email": "test.user@gmail.com", "name": "Test User", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c"},
        {"PK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684", "SK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684", "email": "test.user2@gmail.com", "name": "Test User2", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684"},
        {"PK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d685", "SK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d685", "email": "test.user3@gmail.com", "name": "Test User3", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d685"},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-abcd-abcd-123456789112", "createdAt": "2018-09-01T10:00:00", "listOwner": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "description": "A gift list for Api Childs birthday.", "eventDate": "2019-09-01"},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "SHARE#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-abcd-abcd-123456789112", "createdAt": "2018-09-01T10:00:00", "listOwner": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "description": "A gift list for Api Childs birthday.", "eventDate": "2019-09-01"},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "SHARE#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-abcd-abcd-123456789112", "createdAt": "2018-09-01T10:00:00", "listOwner": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "description": "A gift list for Api Childs birthday.", "eventDate": "2019-09-01"},
        {"PK": "LIST#49d47a66-8825-4872-85c2-e15a12d19aed", "SK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "title": "Oscar's 2019 Christmas List", "occasion": "Christmas", "listId": "49d47a66-8825-4872-85c2-e15a12d19aed", "listOwner": "eu-west-1:1234250a-0fb0-4b32-9842-041c69be1234", "createdAt": "2019-11-01T10:00:00", "description": "A gift list for Oscars Christmas.", "eventDate": "2019-12-25"},
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
        cognito_identity_id = "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684"
        items = get_shared_list.get_list_query('lists-unittest', cognito_identity_id, "12345678-abcd-abcd-123456789112")
        assert len(items) == 6, "Number of items deleted was not as expected."

    def test_get_list_query_no_table_name(self, dynamodb_mock):
        cognito_identity_id = "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684"

        with pytest.raises(Exception) as e:
            get_shared_list.get_list_query('lists-unittes', cognito_identity_id, "12345678-abcd-abcd-123456789112")
        assert str(e.value) == "Unexpected error when getting list item from table.", "Exception not as expected."

    def test_get_list_query_for_item_that_does_not_exist(self, dynamodb_mock):
        cognito_identity_id = "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684"

        with pytest.raises(Exception) as e:
            get_shared_list.get_list_query('lists-unittest', cognito_identity_id, "12345678-abcd-abcd-123456789112-diff")
        assert str(e.value) == "No query results for List ID 12345678-abcd-abcd-123456789112-diff and user: eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684.", "Exception not as expected."


class TestGetSharedListMain:
    def test_get_shared_list_main(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = get_shared_list.get_shared_list_main(api_gateway_get_list_event)
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

    def test_get_shared_list_main_no_table(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = get_shared_list.get_shared_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting list item from table.', "Get list response did not contain the correct error message."

    def test_get_shared_list_when_not_shared_with_requestor(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_get_list_event['requestContext']['identity']['cognitoIdentityId'] = "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d685"

        response = get_shared_list.get_shared_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == "List ID 12345678-abcd-abcd-123456789112 did not have a shared item with user eu-west-1:db9476fd-de77-4977-839f-4f943ff5d685.", "Get list response did not contain the correct error message."


def test_handler(api_gateway_get_list_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = get_shared_list.handler(api_gateway_get_list_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"list": .*}', response['body'])
