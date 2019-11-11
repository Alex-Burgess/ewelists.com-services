import pytest
import os
import re
import json
import copy
import boto3
from moto import mock_dynamodb2
from products import search_url

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_search_event():
    """ Generates API GW Event"""

    return {
        "resource": "/products/url/{url}",
        "path": "/products/url/https%3A%2F%2Fwww.amazon.co.uk%2Fdp%2FB01H24LM58",
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
            "url": "https%3A%2F%2Fwww.amazon.co.uk%2Fdp%2FB01H24LM58"
        },
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/products",
            "httpMethod": "Get",
            "extendedRequestId": "BQGojGkBjoEFsTw=",
            "requestTime": "08/Oct/2019:16:22:40 +0000",
            "path": "/test/products",
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
    table_name = 'products-unittest'

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
                },
                {
                    'AttributeName': 'productUrl', 'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'producturl-index',
                    'KeySchema': [
                         {
                             'AttributeName': 'productUrl', 'KeyType': 'HASH'
                         }
                     ],
                     'Projection': {
                        'ProjectionType': 'ALL'
                     }
                }
            ]
        )

    # 1 User, with 1 list.
    items = [
        {
            "productId": "12345678-prod-0001-1234-abcdefghijkl",
            "brand": "BABYBJÖRN",
            "details": "Travel Cot Easy Go, Anthracite, with transport bag",
            "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
            "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58"
            },
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetUrl:
    def test_get_url(self, api_gateway_search_event):
        url = search_url.get_url(api_gateway_search_event)
        assert url == "https://www.amazon.co.uk/dp/B01H24LM58", "Url returned from API event was not as expected."

    def test_product_id_not_present(self, api_gateway_search_event):
        event_no_path = copy.deepcopy(api_gateway_search_event)
        event_no_path['pathParameters'] = None

        with pytest.raises(Exception) as e:
            search_url.get_url(event_no_path)
        assert str(e.value) == "API Event did not contain a Url in the path parameters.", "Exception not as expected."


class TestUrlQuery:
    def test_url_query(self, dynamodb_mock):
        query_url = 'https://www.amazon.co.uk/dp/B01H24LM58'
        product = search_url.url_query('products-unittest', 'producturl-index', query_url)
        assert product['productId'] == '12345678-prod-0001-1234-abcdefghijkl', "Product Id was not as expected."
        assert product['brand'] == 'BABYBJÖRN', "Brand was not as expected."
        assert product['details'] == 'Travel Cot Easy Go, Anthracite, with transport bag', "Details was not as expected."
        assert product['imageUrl'] == 'https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg', "Img url was not as expected."
        assert product['productUrl'] == 'https://www.amazon.co.uk/dp/B01H24LM58', "Url was not as expected."

    def test_query_with_wrong_table_name(self, dynamodb_mock):
        query_url = 'https://www.amazon.co.uk/dp/B01H24LM58'

        with pytest.raises(Exception) as e:
            search_url.url_query('products-unittes', 'producturl-index', query_url)
        assert str(e.value) == "Unexpected error when searching for product.", "Exception not as expected."

    def test_query_with_product_that_does_not_exist(self, dynamodb_mock):
        query_url = 'https://www.amazon.co.uk/dp/B01H24LM58/missing'
        product = search_url.url_query('products-unittest', 'producturl-index', query_url)
        assert len(product) == 0, "Product was not empty as expected"


class TestSearchMain:
    def test_search_main(self, monkeypatch, api_gateway_search_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'producturl-index')

        response = search_url.search_main(api_gateway_search_event)
        body = json.loads(response['body'])
        assert body['product']['productId'] == '12345678-prod-0001-1234-abcdefghijkl', "Product Id was not as expected."
        assert body['product']['brand'] == 'BABYBJÖRN', "Brand was not as expected."
        assert body['product']['details'] == 'Travel Cot Easy Go, Anthracite, with transport bag', "Details was not as expected."
        assert body['product']['imageUrl'] == 'https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg', "Img url was not as expected."
        assert body['product']['productUrl'] == 'https://www.amazon.co.uk/dp/B01H24LM58', "Url was not as expected."

    def test_with_url_that_does_not_exist(self, monkeypatch, api_gateway_search_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'producturl-index')

        event_no_product = copy.deepcopy(api_gateway_search_event)
        event_no_product['pathParameters']['url'] = 'https://www.amazon.co.uk/dp/B01H24LM58/missing'

        response = search_url.search_main(event_no_product)
        body = json.loads(response['body'])
        assert len(body['product']) == 0, "Number of products returned was not 0"

    def test_wrong_table_returns_error(self, monkeypatch, api_gateway_search_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittes')
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'producturl-index')

        response = search_url.search_main(api_gateway_search_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when searching for product.', "Get list response did not contain the correct error message."


def test_handler(api_gateway_search_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'products-unittest')
    monkeypatch.setitem(os.environ, 'INDEX_NAME', 'producturl-index')
    response = search_url.handler(api_gateway_search_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"product": .*}', response['body'])


class TestAmazonUrls:
    def test_remove_url_params(self):
        query_url = 'https://www.amazon.co.uk/dp/B01H24LM58?ref_=ams_ad_dp_asin_img'
        url = search_url.parse_url(query_url)
        assert url == "https://www.amazon.co.uk/dp/B01H24LM58", "Parsed url was not as expected."

    def test_remove_url_params2(self):
        query_url = 'https://www.amazon.co.uk/BABYBJ%C3%96RN-Travel-Easy-Anthracite-transport/dp/B07DJ5KX53/ref=pd_bxgy_75_img_2/257-8649096-9647520?_encoding=UTF8&pd_rd_i=B07DJ5KX53&pd_rd_r=cff83e81-8002-4ed1-8b75-d88d7ac71ed6&pd_rd_w=OTmbK&pd_rd_wg=FGU6l&pf_rd_p=655b7c7d-a17d-4637-9a0a-72a813e0d2cb&pf_rd_r=E53ZAGTW3PSQ3PJ6YQQR&psc=1&refRID=E53ZAGTW3PSQ3PJ6YQQR'
        url = search_url.parse_url(query_url)
        assert url == "https://www.amazon.co.uk/dp/B07DJ5KX53", "Parsed url was not as expected."
