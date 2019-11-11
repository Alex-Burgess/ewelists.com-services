import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import delete_product

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_delete_product_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists/{id}/product/{productid}",
        "path": "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl",
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
            "productid": "12345678-prod-0001-1234-abcdefghijkl",
            "id": "12345678-list-0001-1234-abcdefghijkl"
        },
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/lists/{id}/product/{productid}",
            "httpMethod": "DELETE",
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
        "body": "{\n    \"productType\": \"products\"\n}",
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
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "description": "A gift list for Api Childs birthday.", "eventDate": "01 September 2019"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl", "type": "products", "quantity": 1, "reserved": 1}
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestDeleteProductItem:
    def test_delete_product_item(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        result = delete_product.delete_product_item('lists-unittest', list_id, product_id)
        assert result, "Product was not deleted from table."

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        test_response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={'PK': {'S': "LIST#" + list_id}, 'SK': {'S': "PRODUCT#" + product_id}}
        )

        assert 'Item' not in test_response, "Product ID should not exist."

    def test_delete_product_item_with_no_table(self, dynamodb_mock):
        product_id = '12345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete_product.delete_product_item('lists-unittes', list_id, product_id)
        assert str(e.value) == "Product could not be deleted.", "Exception not as expected."

    @pytest.mark.skip(reason="Moto is not throwing an exception when deleting with ConditionExpression")
    def test_delete_non_existent_product_item(self, dynamodb_mock):
        product_id = '112345678-prod-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete_product.delete_product_item('lists-unittest', list_id, product_id)
        assert str(e.value) == "Product could not be deleted.", "Exception not as expected."


class TestDeleteProductMain:
    def test_delete_product(self, api_gateway_delete_product_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = delete_product.delete_product_main(api_gateway_delete_product_event)
        body = json.loads(response['body'])
        assert body['message'], "Delete product main response did not contain the correct status."

    def test_delete_product_with_not_owner(self, api_gateway_delete_product_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_delete_product_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"
        response = delete_product.delete_product_main(api_gateway_delete_product_event)
        body = json.loads(response['body'])
        assert body['error'] == "No list exists with this ID.", "Error not as expected."

    def test_delete_product_with_no_list_id(self, api_gateway_delete_product_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_delete_product_event['pathParameters']['id'] = '12345678-list-0002-1234-abcdefghijkl'
        response = delete_product.delete_product_main(api_gateway_delete_product_event)
        body = json.loads(response['body'])
        assert body['error'] == "No list exists with this ID.", "Error not as expected."

    def test_delete_product_with_no_product_id(self, api_gateway_delete_product_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_delete_product_event['pathParameters']['productid'] = None
        response = delete_product.delete_product_main(api_gateway_delete_product_event)
        body = json.loads(response['body'])
        assert body['error'] == "API Event did not contain a Product ID in the path parameters.", "Error not as expected."

def test_handler(api_gateway_delete_product_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = delete_product.handler(api_gateway_delete_product_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    assert re.match('{"message": .*}', response['body']), "Response body was not as expected."
