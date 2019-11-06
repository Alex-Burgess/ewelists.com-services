import pytest
import os
import re
import json
import copy
import boto3
from moto import mock_dynamodb2
from notfound import create

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_create_event():
    """ Generates API GW Event"""

    return {
        "resource": "/notfound",
        "path": "/notfound",
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
        "pathParameters": "null",
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/notfound",
            "httpMethod": "POST",
            "extendedRequestId": "BQGojGkBjoEFsTw=",
            "requestTime": "08/Oct/2019:16:22:40 +0000",
            "path": "/test/notfound",
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
        "body": "{\n    \"brand\": \"BABYBJÖRN\",\n    \"details\": \"Travel Cot Easy Go, Anthracite, with transport bag\",\n    \"url\": \"https://www.amazon.co.uk/dp/B01H24LM58\"\n}",
        "isBase64Encoded": "false"
    }


@pytest.fixture
def dynamodb_mock():
    table_name = 'notfound-unittest'

    mock = mock_dynamodb2()
    mock.start()

    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'productId', 'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'productId', 'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5
            }
        )

    # 1 User, with 1 list.
    items = [
        {"productId": "12345678-notf-0010-1234-abcdefghijkl", "brand": "John Lewis", "details": "John Lewis & Partners Safari Mobile", "url": "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165"},
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetProductInfo:
    def test_get_product_info(self, api_gateway_create_event):
        product_info = create.get_product_info(api_gateway_create_event)
        assert product_info['brand'] == "BABYBJÖRN", "Attribute brand was not as expected."
        assert product_info['details'] == "Travel Cot Easy Go, Anthracite, with transport bag", "Attribute details was not as expected."
        assert product_info['url'] == "https://www.amazon.co.uk/dp/B01H24LM58", "Attribute url was not as expected."

    def test_with_empty_body_throws_exception(self, api_gateway_create_event):
        event_no_body = copy.deepcopy(api_gateway_create_event)
        event_no_body['body'] = None

        with pytest.raises(Exception) as e:
            create.get_product_info(event_no_body)
        assert str(e.value) == "API Event did not contain a valid body.", "Exception not as expected."


class TestPutProduct:
    def test_put_product(self, dynamodb_mock):
        cognito_user_id = '12345678-user-0001-1234-abcdefghijkl'
        product_info = {
            'brand': 'Mamas & Papas',
            'details': 'Hilston Nursing Chair - Silver',
            'url': 'https://www.mamasandpapas.com/en-gb/hilston-nursing-chair-duck-egg/p/chnsoa100',
        }

        product_id = create.put_product('notfound-unittest', cognito_user_id, product_info)
        assert len(product_id) == 36, 'Product ID not expected length.'

    def test_bad_table_name_throws_exception(self, dynamodb_mock):
        cognito_user_id = '12345678-user-0001-1234-abcdefghijkl'
        product_info = {
            'brand': 'Mamas & Papas',
            'details': 'Hilston Nursing Chair - Silver',
            'url': 'https://www.mamasandpapas.com/en-gb/hilston-nursing-chair-duck-egg/p/chnsoa100',
        }

        with pytest.raises(Exception) as e:
            create.put_product('notfound-unittes', cognito_user_id, product_info)
        assert str(e.value) == "Product could not be created.", "Exception not as expected."


class TestCreateMain:
    def test_create_main(self, monkeypatch, api_gateway_create_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')

        response = create.create_main(api_gateway_create_event)
        body = json.loads(response['body'])

        assert len(body['productId']) == 36, "Create main response did not contain a listId."

    def test_with_no_event_body(self, monkeypatch, api_gateway_create_event, dynamodb_mock):
        event_no_body = copy.deepcopy(api_gateway_create_event)
        event_no_body['body'] = None
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')

        response = create.create_main(event_no_body)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event did not contain a valid body.', "Create main response did not contain the correct error message."


def test_handler(api_gateway_create_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-unittest')
    response = create.handler(api_gateway_create_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"productId": .*}', response['body'])
