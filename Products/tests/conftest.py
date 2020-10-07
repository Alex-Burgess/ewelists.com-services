import pytest
import boto3
from moto import mock_dynamodb2


@pytest.fixture
def empty_table():
    with mock_dynamodb2():
        table_name = 'products-unittest'

        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        yield dynamodb


@pytest.fixture
def table():
    with mock_dynamodb2():
        table_name = 'products-unittest'

        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
                AttributeDefinitions=[
                    {'AttributeName': 'productId', 'AttributeType': 'S'},
                    {'AttributeName': 'productUrl', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'producturl-index',
                        'KeySchema': [{'AttributeName': 'productUrl', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )

        items = [
            {
                "productId": "12345678-prod-0001-1234-abcdefghijkl",
                "retailer": "amazon.co.uk",
                "brand": "BABYBJÖRN",
                "details": "Travel Cot Easy Go, Anthracite, with transport bag",
                "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
                "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
                "price": "100.00"
            },
            {
                "productId": "12345678-prod-0002-1234-abcdefghijkl",
                "brand": "John Lewis & Partners",
                "details": "Baby GOTS Organic Cotton Elephant Sleepsuit, Pack of 3, White",
                "price": "13.00",
                "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/003953444?$rsp-pdp-port-640$",
                "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-gots-organic-cotton-elephant-sleepsuit-pack-of-3-white/p4233425"
            },
            {
                "productId": "12345678-prod-0003-1234-abcdefghijkl",
                "retailer": "amazon.co.uk",
                "brand": "BABYBJÖRN",
                "details": "Travel Cot Easy Go, Anthracite, with transport bag",
                "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
                "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58"
            }
        ]

        for item in items:
            table.put_item(TableName=table_name, Item=item)

        yield


@pytest.fixture
def api_gateway_with_id_event():
    event = api_gateway_base_event()
    event['resource'] = "/products/{id}"
    event['path'] = "/products/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-prod-0001-1234-abcdefghijkl"}
    event['body'] = "null"

    return event


@pytest.fixture
def api_gateway_event_with_no_product_id():
    event = api_gateway_base_event()
    event['resource'] = "/products"
    event['path'] = "/products"
    event['httpMethod'] = "POST"

    return event


@pytest.fixture
def api_create_event():
    event = api_gateway_base_event()
    event['httpMethod'] = "POST"
    event['body'] = "{\n    \"retailer\": \"amazon.co.uk\",\n    \"brand\": \"BABYBJÖRN\",\n    \"details\": \"Travel Cot Easy Go, Anthracite, with transport bag\",\n    \"productUrl\": \"https://www.amazon.co.uk/dp/B01H24LM58\",\n    \"imageUrl\": \"https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg\"\n}"

    return event


@pytest.fixture
def api_create_with_price_event():
    event = api_gateway_base_event()
    event['httpMethod'] = "POST"
    event['body'] = "{\n    \"retailer\": \"amazon.co.uk\",\n    \"price\": \"100.00\",\n    \"brand\": \"BABYBJÖRN\",\n    \"details\": \"Travel Cot Easy Go, Anthracite, with transport bag\",\n    \"productUrl\": \"https://www.amazon.co.uk/dp/B01H24LM58\",\n    \"imageUrl\": \"https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg\"\n}"

    return event


@pytest.fixture
def api_gateway_delete_event():
    event = api_gateway_base_event()
    event['resource'] = "/products/{id}"
    event['path'] = "/products/12345678-prod-0010-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"id": "12345678-prod-0010-1234-abcdefghijkl"}

    return event


@pytest.fixture
def api_gateway_get_product_event():
    event = api_gateway_base_event()
    event['resource'] = "/products/{id}"
    event['path'] = "/products/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-prod-0001-1234-abcdefghijkl"}
    event['body'] = "null"

    return event


@pytest.fixture
def api_gateway_search_event():
    event = api_gateway_base_event()
    event['resource'] = "/products/url/{url}"
    event['path'] = "/products/url/https%3A%2F%2Fwww.amazon.co.uk%2Fdp%2FB01H24LM58"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"url": "https%3A%2F%2Fwww.amazon.co.uk%2Fdp%2FB01H24LM58"}
    event['body'] = "null"

    return event


def api_gateway_base_event():
    """ Generates API GW Event"""

    return {
        "resource": "/products",
        "path": "/products",
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
            "resourcePath": "/products",
            "httpMethod": "GET",
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
