import pytest
import boto3
import json
from moto import mock_dynamodb2


@pytest.fixture
def table():
    with mock_dynamodb2():
        table_name = 'notfound-unittest'

        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )

        items = [
            {
                "productId": "12345678-notf-0010-1234-abcdefghijkl",
                "brand": "John Lewis",
                "details": "John Lewis & Partners Safari Mobile",
                "productUrl": "https://www.johnlewis.com/john-lewis-partners-safari-mobile/p3439165",
                "createdBy": "12345678-user-0001-1234-abcdefghijkl"
            },
            {
               "productId": "12345678-notf-0020-1234-abcdefghijkl",
               "brand": "The White Company",
               "details": "Halden Champagne Flutes – Set Of 4",
               "productUrl": "https://www.thewhitecompany.com/uk/Halden-Champagne-Flutes--Set-of-4/p/GWHSC",
               "imageUrl": "https://whitecompany.scene7.com/is/image/whitecompany/Halden-Champagne-Flutes---Set-of-4/GWHSC_2_MAIN?$D_PDP_412x412$",
               "price": "40.00",
               "createdBy": "12345678-user-0001-1234-abcdefghijkl"
            }
        ]

        for item in items:
            table.put_item(TableName=table_name, Item=item)

        yield


@pytest.fixture
def api_gateway_create_event():
    event = api_gateway_base_event()
    event['httpMethod'] = "POST"
    event['body'] = json.dumps({
        "brand": "BABYBJÖRN",
        "details": "Travel Cot Easy Go, Anthracite, with transport bag",
        "url": "https://www.amazon.co.uk/dp/B01H24LM58"
    })

    return event


@pytest.fixture
def api_gateway_create_all_event():
    event = api_gateway_base_event()
    event['httpMethod'] = "POST"
    event['body'] = json.dumps({
        "brand": "BABYBJÖRN",
        "details": "Travel Cot Easy Go, Anthracite, with transport bag",
        "url": "https://www.amazon.co.uk/dp/B01H24LM58",
        "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
        "price": "100.00"
    })

    return event


@pytest.fixture
def api_gateway_delete_event():
    event = api_gateway_base_event()
    event['resource'] = "/notfound/{id}"
    event['path'] = "/notfound/12345678-notf-0010-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"id": "12345678-notf-0010-1234-abcdefghijkl"}

    return event


@pytest.fixture
def api_gateway_get_product_event():
    event = api_gateway_base_event()
    event['resource'] = "/notfound/{id}"
    event['path'] = "/notfound/12345678-notf-0010-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-notf-0010-1234-abcdefghijkl"}

    return event


@pytest.fixture
def api_gateway_with_id_event():
    event = api_gateway_base_event()
    event['resource'] = "/notfound/{id}"
    event['path'] = "/notfound/12345678-notf-0010-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-notf-0010-1234-abcdefghijkl"}
    event['body'] = "null"

    return event


@pytest.fixture
def api_gateway_postman_event():
    event = api_gateway_base_event()
    event['resource'] = "/notfound/{id}"
    event['path'] = "/notfound/12345678-notf-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-notf-0001-1234-abcdefghijkl"}
    event['body'] = "null"

    event['requestContext']['identity'] = {
        "cognitoIdentityPoolId": "null",
        "accountId": "123456789012",
        "cognitoIdentityId": "null",
        "caller": "ABCDEFGPDMJL4EB35H6H",
        "sourceIp": "5.81.150.55",
        "principalOrgId": "o-d8jj6dyqv2",
        "accessKey": "ABCDEFGPDMJL4EB35H6H",
        "cognitoAuthenticationType": "null",
        "cognitoAuthenticationProvider": "null",
        "userArn": "arn:aws:iam::123456789012:user/ApiTestUser",
        "userAgent": "PostmanRuntime/7.15.2",
        "user": "ABCDEFGPDMJL4EB35H6H"
    }

    return event


@pytest.fixture
def api_gateway_event_with_no_identity():
    event = api_gateway_base_event()
    event['resource'] = "/notfound/{id}"
    event['path'] = "/notfound/12345678-notf-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-notf-0001-1234-abcdefghijkl"}
    event['body'] = "null"
    event['requestContext']['identity'] = {}

    return event


@pytest.fixture
def api_gateway_event_with_no_product_id():
    event = api_gateway_base_event()
    event['resource'] = "/notfound"
    event['path'] = "/notfound"
    event['httpMethod'] = "GET"

    return event


def api_gateway_base_event():
    """ Generates API GW Event"""

    return {
        "resource": "/notfound",
        "path": "/notfound",
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
            "resourcePath": "/notfound",
            "httpMethod": "GET",
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
        "body": "null",
        "isBase64Encoded": "false"
    }
