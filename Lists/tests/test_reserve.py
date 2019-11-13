import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import reserve

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_reserve_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists/{id}/reserve/{productid}",
        "path": "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl",
        "httpMethod": "POST",
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
            "productid": "12345678-prod-0001-1234-abcdefghijkl",
            "id": "12345678-list-0001-1234-abcdefghijkl"
        },
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/lists/{id}/product/{productid}",
            "httpMethod": "POST",
            "extendedRequestId": "BQGojGkBjoEFsTw=",
            "requestTime": "08/Oct/2019:16:22:40 +0000",
            "path": "/test/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl",
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
        "body": "{\n    \"quantity\": 2,\n    \"message\": \"Happy birthday to you!\",\n    \"userId\": \"12345678-user-0003-1234-abcdefghijkl\"\n}",
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
                    'AttributeName': 'PK', 'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'SK', 'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'PK', 'AttributeType': 'S'
                },
                {
                    'AttributeName': 'SK', 'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5
            }
        )

    # 1 User, with 1 list.
    items = [
        {"PK": "USER#12345678-user-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "email": "test.user@gmail.com", "name": "Test User", "userId": "12345678-user-0001-1234-abcdefghijkl"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl", "type": "products", "quantity": 1, "reserved": 0, "reservedDetails": [{"name": "Test User"}]},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#12345678-prod-0002-1234-abcdefghijkl", "type": "products", "quantity": 2, "reserved": 1}
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetUsersName:
    def test_get_users_name(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        name = reserve.get_users_name('lists-unittest', user_id)
        assert name == "Test User", "User's name was not as expected."

    def test_with_invalid_userid(self, dynamodb_mock):
        user_id = '12345678-user-0010-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            reserve.get_users_name('lists-unittest', user_id)
        assert str(e.value) == "No user exists with this ID.", "Exception not as expected."


class TestGetProductQuantities:
    def test_get_product_quantities(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        quantities = reserve.get_product_quantities('lists-unittest', list_id, product_id)

        expected_result = {'quantity': 1, 'reserved': 0}
        assert quantities == expected_result, "Quantities not as expected."

    def test_with_invalid_productid(self, dynamodb_mock):
        product_id = '12345678-prod-0010-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            reserve.get_product_quantities('lists-unittest', list_id, product_id)
        assert str(e.value) == "No product exists with this ID.", "Exception not as expected."


class TestUpdateReservedQuantities:
    def test_with_no_update(self):
        quantities = {'quantity': 1, 'reserved': 0}
        assert reserve.update_reserved_quantities(quantities, 0)

    def test_reserve_one_product(self):
        quantities = {'quantity': 1, 'reserved': 0}
        assert reserve.update_reserved_quantities(quantities, 0)

    def test_reserve_two_product(self):
        quantities = {'quantity': 2, 'reserved': 0}
        assert reserve.update_reserved_quantities(quantities, 2)

    def test_over_reserve(self):
        quantities = {'quantity': 1, 'reserved': 1}
        with pytest.raises(Exception) as e:
            reserve.update_reserved_quantities(quantities, 1)
        assert str(e.value) == "Reserved product quantity 2 exceeds quantity required 1."

    def test_over_reserve2(self):
        quantities = {'quantity': 1, 'reserved': 0}
        with pytest.raises(Exception) as e:
            reserve.update_reserved_quantities(quantities, 2)
        assert str(e.value) == "Reserved product quantity 2 exceeds quantity required 1."


class TestAddReservedDetails:
    def test_add_reserved_details(self, dynamodb_mock):
        table_name = 'lists-unittest'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        users_name = 'Test User'
        user_reserved = 1
        total_reserved = 1
        message = 'A test message'
        assert reserve.add_reserved_details(table_name, list_id, product_id, user_id, users_name, user_reserved, total_reserved, message)

        # Check the table was updated with right reserved details
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        print("reserved details: " + json.dumps(test_response['Item']['reservedDetails']))

        reserved_quantity = int(test_response['Item']['reserved']['N'])
        reserved_details = test_response['Item']['reservedDetails']['L']
        reserved_obj = reserved_details[1]['M']

        assert reserved_quantity == 1, "Quantity not as expected."
        assert len(reserved_details) == 2, "Number of reserved details was not as expected."
        assert reserved_obj['name']['S'] == 'Test User', "Reserved name was not as expected."
        assert reserved_obj['userId']['S'] == '12345678-user-0001-1234-abcdefghijkl', "UserId was not as expected."
        assert reserved_obj['reserved']['N'] == '1', "Reserved quantity was not as expected."
        assert reserved_obj['message']['S'] == 'A test message', "Message was not as expected."
        assert len(reserved_obj['reservedAt']['N']) == 10, "Message was not as expected."

    def test_when_reservedDetails_not_present(self, dynamodb_mock):
        table_name = 'lists-unittest'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        users_name = 'Test User'
        user_reserved = 1
        total_reserved = 1
        message = 'A test message'
        assert reserve.add_reserved_details(table_name, list_id, product_id, user_id, users_name, user_reserved, total_reserved, message)

        # Check the table was updated with right reserved details
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        print("reserved details: " + json.dumps(test_response['Item']['reservedDetails']))

        reserved_quantity = int(test_response['Item']['reserved']['N'])
        reserved_details = test_response['Item']['reservedDetails']['L']
        reserved_obj = reserved_details[0]['M']

        assert reserved_quantity == 1, "Quantity not as expected."
        assert len(reserved_details) == 1, "Number of reserved details was not as expected."
        assert reserved_obj['name']['S'] == 'Test User', "Reserved name was not as expected."
