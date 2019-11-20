import pytest
import os
from lists import common
import sys
import copy
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture()
def api_gateway_with_id_event():
    """ Generates API GW Event"""

    return {
      "resource": "/lists/{id}",
      "path": "/lists/12345678-list-0001-1234-abcdefghijkl",
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
          "id": "12345678-list-0001-1234-abcdefghijkl"
      },
      "stageVariables": "null",
      "requestContext": {
          "resourceId": "4j13uq",
          "resourcePath": "/lists/{id}",
          "httpMethod": "GET",
          "extendedRequestId": "BMsiDFARjoEFgOg=",
          "requestTime": "07/Oct/2019:15:33:45 +0000",
          "path": "/test/lists/12345678-list-0001-1234-abcdefghijkl",
          "accountId": "123456789012",
          "protocol": "HTTP/1.1",
          "stage": "test",
          "domainPrefix": "4sdcvv0n2e",
          "requestTimeEpoch": 1570462425886,
          "requestId": "4fa38ad5-1706-4bdb-b0e2-6a5519cc12fa",
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


@pytest.fixture()
def api_gateway_event_with_no_list_id():
    """ Generates API GW Event"""

    return {
        "resource": "/lists",
        "path": "/lists",
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
            "resourcePath": "/lists",
            "httpMethod": "POST",
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


@pytest.fixture()
def api_gateway_postman_event():
    """ Generates API GW Event"""

    return {
      "resource": "/lists/{id}",
      "path": "/lists/12345678-list-0001-1234-abcdefghijkl",
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
          "id": "12345678-list-0001-1234-abcdefghijkl"
      },
      "stageVariables": "null",
      "requestContext": {
          "resourceId": "4j13uq",
          "resourcePath": "/lists/{id}",
          "httpMethod": "GET",
          "extendedRequestId": "BMsiDFARjoEFgOg=",
          "requestTime": "07/Oct/2019:15:33:45 +0000",
          "path": "/test/lists/12345678-list-0001-1234-abcdefghijkl",
          "accountId": "123456789012",
          "protocol": "HTTP/1.1",
          "stage": "test",
          "domainPrefix": "4sdcvv0n2e",
          "requestTimeEpoch": 1570462425886,
          "requestId": "4fa38ad5-1706-4bdb-b0e2-6a5519cc12fa",
          "identity": {
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
          },
          "domainName": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
          "apiId": "4sdcvv0n2e"
      },
      "body": "null",
      "isBase64Encoded": "false"
    }


@pytest.fixture()
def api_gateway_event_with_no_identity():
    """ Generates API GW Event"""

    return {
      "resource": "/lists/{id}",
      "path": "/lists/12345678-list-0001-1234-abcdefghijkl",
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
          "id": "12345678-list-0001-1234-abcdefghijkl"
      },
      "stageVariables": "null",
      "requestContext": {
          "resourceId": "4j13uq",
          "resourcePath": "/lists/{id}",
          "httpMethod": "GET",
          "extendedRequestId": "BMsiDFARjoEFgOg=",
          "requestTime": "07/Oct/2019:15:33:45 +0000",
          "path": "/test/lists/12345678-list-0001-1234-abcdefghijkl",
          "accountId": "123456789012",
          "protocol": "HTTP/1.1",
          "stage": "test",
          "domainPrefix": "4sdcvv0n2e",
          "requestTimeEpoch": 1570462425886,
          "requestId": "4fa38ad5-1706-4bdb-b0e2-6a5519cc12fa",
          "identity": {},
          "domainName": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
          "apiId": "4sdcvv0n2e"
      },
      "body": "null",
      "isBase64Encoded": "false"
    }


@pytest.fixture
def api_gateway_add_product_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists/{id}/product/{productid}",
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
        "body": "{\n    \"quantity\": 1,\n    \"productType\": \"products\"\n}",
        "isBase64Encoded": "false"
    }


@pytest.fixture()
def example_response():
    # Example response for a list, with user 2 as owner, shared with users 3, 4 and 5 and a pending user 6. 1 product not reserved, 1 product reserved by user 5.
    example_response = [
        {"occasion": {"S": "Birthday"}, "listId": {"S": "12345678-list-0002-1234-abcdefghijkl"}, "eventDate": {"S": "31 October 2018"}, "listOwner": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "createdAt": {"S": "2018-09-01T10:00:00"}, "SK": {"S": "PENDING#test.user6@gmail.com"}, "description": {"S": "A gift list for Oscars birthday."}, "PK": {"S": "LIST#12345678-list-0002-1234-abcdefghijkl"}, "email": {"S": "test.user6@gmail.com"}, "title": {"S": "Oscar's 1st Birthday"}},
        {"quantity": {"N": "1"}, "reserved": {"N": "0"}, "type": {"S": "products"}, "SK": {"S": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "PK": {"S": "LIST#12345678-list-0002-1234-abcdefghijkl"}},
        {"quantity": {"N": "2"}, "reserved": {"N": "1"}, "type": {"S": "notfound"}, "SK": {"S": "PRODUCT#12345678-prod-0002-1234-abcdefghijkl"}, "PK": {"S": "LIST#12345678-list-0002-1234-abcdefghijkl"}, "reservedDetails": {"L": [{"M": {"name": {"S": "Test User"}, "userId": {"S": "12345678-user-0005-1234-abcdefghijkl"}, "reservedNumber": {"N": "1"}, "message": {"S": "Happy Birthday"}, "reservedAt": {"N": "1573739584"}}}]}},
        {"occasion": {"S": "Birthday"}, "listId": {"S": "12345678-list-0002-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0003-1234-abcdefghijkl"}, "eventDate": {"S": "31 October 2018"}, "listOwner": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "createdAt": {"S": "2018-09-01T10:00:00"}, "SK": {"S": "SHARE#12345678-user-0003-1234-abcdefghijkl"}, "description": {"S": "A gift list for Oscars birthday."}, "PK": {"S": "LIST#12345678-list-0002-1234-abcdefghijkl"}, "title": {"S": "Oscar's 1st Birthday"}},
        {"occasion": {"S": "Birthday"}, "listId": {"S": "12345678-list-0002-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0004-1234-abcdefghijkl"}, "eventDate": {"S": "31 October 2018"}, "listOwner": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "createdAt": {"S": "2018-09-01T10:00:00"}, "SK": {"S": "SHARE#12345678-user-0004-1234-abcdefghijkl"}, "description": {"S": "A gift list for Oscars birthday."}, "PK": {"S": "LIST#12345678-list-0002-1234-abcdefghijkl"}, "title": {"S": "Oscar's 1st Birthday"}, "imageUrl": {"S": "/images/celebration-default.jpg"}},
        {"occasion": {"S": "Birthday"}, "listId": {"S": "12345678-list-0002-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0005-1234-abcdefghijkl"}, "eventDate": {"S": "31 October 2018"}, "listOwner": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "createdAt": {"S": "2018-09-01T10:00:00"}, "SK": {"S": "SHARE#12345678-user-0005-1234-abcdefghijkl"}, "description": {"S": "A gift list for Oscars birthday."}, "PK": {"S": "LIST#12345678-list-0002-1234-abcdefghijkl"}, "title": {"S": "Oscar's 1st Birthday"}, "imageUrl": {"S": "/images/celebration-default.jpg"}},
        {"occasion": {"S": "Birthday"}, "listId": {"S": "12345678-list-0002-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "eventDate": {"S": "31 October 2018"}, "listOwner": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "createdAt": {"S": "2018-09-01T10:00:00"}, "SK": {"S": "SHARE#12345678-user-0002-1234-abcdefghijkl"}, "description": {"S": "A gift list for Oscars birthday."}, "PK": {"S": "LIST#12345678-list-0002-1234-abcdefghijkl"}, "title": {"S": "Oscar's 1st Birthday"}, "imageUrl": {"S": "/images/celebration-default.jpg"}},
        {"occasion": {"S": "Birthday"}, "listId": {"S": "12345678-list-0002-1234-abcdefghijkl"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "eventDate": {"S": "31 October 2018"}, "listOwner": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "createdAt": {"S": "2018-09-01T10:00:00"}, "SK": {"S": "USER#12345678-user-0002-1234-abcdefghijkl"}, "description": {"S": "A gift list for Oscars birthday."}, "PK": {"S": "LIST#12345678-list-0002-1234-abcdefghijkl"}, "title": {"S": "Oscar's 1st Birthday"}, "imageUrl": {"S": "/images/celebration-default.jpg"}}
    ]

    return example_response


def test_create_response():
    response = common.create_response(200, 'Success message')

    expected_response = {'statusCode': 200,
                         'body': 'Success message',
                         'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                         }}
    assert response == expected_response, "Create_response did not return the expected response value."


class TestGetListIdFromPath:
    def test_get_list_id(self, api_gateway_with_id_event):
        list_id = common.get_list_id(api_gateway_with_id_event)
        assert list_id == "12345678-list-0001-1234-abcdefghijkl", "List ID returned from API event was not as expected."

    def test_get_list_id_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common.get_list_id(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain a List ID in the path parameters.", "Exception not as expected."

    def test_get_list_id_empty(self, api_gateway_with_id_event):
        api_gateway_with_id_event['pathParameters']['id'] = ''
        with pytest.raises(Exception) as e:
            common.get_list_id(api_gateway_with_id_event)
        assert str(e.value) == "API Event did not contain a List ID in the path parameters.", "Exception not as expected."


class TestGetProductIdFromPath:
    def test_get_product_id(self, api_gateway_add_product_event):
        product_id = common.get_product_id(api_gateway_add_product_event)
        assert product_id == "12345678-prod-0001-1234-abcdefghijkl", "Product ID returned from API event was not as expected."

    def test_get_product_id_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common.get_product_id(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain a Product ID in the path parameters.", "Exception not as expected."

    def test_get_product_id_empty(self, api_gateway_add_product_event):
        api_gateway_add_product_event['pathParameters']['productid'] = ''
        with pytest.raises(Exception) as e:
            common.get_product_id(api_gateway_add_product_event)
        assert str(e.value) == "API Event did not contain a Product ID in the path parameters.", "Exception not as expected."


class TestGetQuantity:
    def test_get_quantity(self, api_gateway_add_product_event):
        quantity = common.get_quantity(api_gateway_add_product_event)
        assert quantity == 1, "Quantity returned from API event was not as expected."

    def test_get_quantity_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common.get_quantity(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain the quantity in the body.", "Exception not as expected."


class TestGetProductType:
    def test_get_product_type(self, api_gateway_add_product_event):
        product = common.get_product_type(api_gateway_add_product_event)
        assert product == 'products', "Product type returned from API event was not as expected."

    def test_get_product_type_of_notfound(self, api_gateway_add_product_event):
        notfound_body = copy.deepcopy(api_gateway_add_product_event)
        notfound_body['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"notfound\"\n}'
        product = common.get_product_type(notfound_body)
        assert product == 'notfound', "Product type returned from API event was not as expected."

    def test_get_wrong_product_type(self, api_gateway_add_product_event):
        wrong_body = copy.deepcopy(api_gateway_add_product_event)
        wrong_body['body'] = '{\n    \"quantity\": 1,\n    \"productType\": \"wrong\"\n}'
        with pytest.raises(Exception) as e:
            common.get_product_type(wrong_body)
        assert str(e.value) == "API Event did not contain a product type of products or notfound.", "Exception not as expected."

    def test_get_product_type_when_not_present(self, api_gateway_event_with_no_list_id):
        with pytest.raises(Exception) as e:
            common.get_product_type(api_gateway_event_with_no_list_id)
        assert str(e.value) == "API Event did not contain the product type in the body.", "Exception not as expected."


class TestGetPostmanIdentity:
    def test_get_postman_identity(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_IDENTITY_ID', 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl')
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')

        identity = common.get_postman_identity(os.environ)
        assert identity['POSTMAN_IDENTITY_ID'] == 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl', "POSTMAN_IDENTITY_ID not as expected."
        assert identity['POSTMAN_USERPOOL_SUB'] == '12345678-user-api1-1234-abcdefghijkl', "POSTMAN_USERPOOL_SUB not as expected."

    def test_get_postman_identity_when_both_osvars_missing(self):
        with pytest.raises(Exception) as e:
            common.get_postman_identity(os.environ)
        assert str(e.value) == "POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."

    def test_get_postman_identity_when_userpool_missing(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_IDENTITY_ID', 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl')
        with pytest.raises(Exception) as e:
            common.get_postman_identity(os.environ)
        assert str(e.value) == "POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."

    def test_get_postman_identity_when_identity_id_missing(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')
        with pytest.raises(Exception) as e:
            common.get_postman_identity(os.environ)
        assert str(e.value) == "POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."


class TestGetIdentity:
    def test_get_identity(self, api_gateway_with_id_event):
        identity = common.get_identity(api_gateway_with_id_event, os.environ)
        assert identity["cognitoIdentityId"] == "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "cognitoIdentityId not as expected."
        assert identity["userPoolSub"] == "12345678-user-0001-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_postman_request(self, monkeypatch, api_gateway_postman_event):
        monkeypatch.setitem(os.environ, 'POSTMAN_IDENTITY_ID', 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl')
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')
        identity = common.get_identity(api_gateway_postman_event, os.environ)
        assert identity["cognitoIdentityId"] == "eu-west-1:12345678-user-fed1-1234-abcdefghijkl", "cognitoIdentityId not as expected."
        assert identity["userPoolSub"] == "12345678-user-api1-1234-abcdefghijkl", "userPoolSub not as expected."

    def test_get_identity_when_noid(self, api_gateway_event_with_no_identity):
        with pytest.raises(Exception) as e:
            common.get_identity(api_gateway_event_with_no_identity, os.environ)
        assert str(e.value) == "There was no identity context in API event.", "Exception not as expected."

    def test_get_identity_when_postman_request_and_with_no_osvars(self, api_gateway_postman_event):
        with pytest.raises(Exception) as e:
            common.get_identity(api_gateway_postman_event, os.environ)
        assert str(e.value) == "POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."


class TestGetTableName:
    def test_get_table_name(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-test')
        table_name = common.get_table_name(os.environ)
        assert table_name == "lists-test", "Table name from os environment variables was not as expected."

    def test_get_table_name_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_table_name(os.environ)
        assert str(e.value) == "TABLE_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetTableIndex:
    def test_get_table_index(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'index-test')
        index_name = common.get_table_index(os.environ)
        assert index_name == "index-test", "Index name from os environment variables was not as expected."

    def test_get_table_index_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_table_index(os.environ)
        assert str(e.value) == "INDEX_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetUserpoolId:
    def test_get_userpool_id(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'USERPOOL_ID', 'ewelists-test')
        userpool_id = common.get_userpool_id(os.environ)
        assert userpool_id == "ewelists-test", "Table name from os environment variables was not as expected."

    def test_get_userpool_name_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_userpool_id(os.environ)
        assert str(e.value) == "USERPOOL_ID environment variable not set correctly.", "Exception not as expected."


class TestConfirmOwner:
    def test_confirm_owner(self, example_response):
        cognito_user_id = '12345678-user-0002-1234-abcdefghijkl'
        list_id = '12345678-list-0002-1234-abcdefghijkl'
        result = common.confirm_owner(cognito_user_id, list_id, example_response)
        assert result, "List should be owned by user."

    def test_confirm_not_owner(self, example_response):
        cognito_user_id = 'eu-west-1:dc7b5ba3-835f-4859-ae67-06af31c2ce03'
        list_id = '12345678-list-0002-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            common.confirm_owner(cognito_user_id, list_id, example_response)
        assert str(e.value) == "Owner of List ID 12345678-list-0002-1234-abcdefghijkl did not match user id of requestor: eu-west-1:dc7b5ba3-835f-4859-ae67-06af31c2ce03.", "Exception not thrown for list not being owned by user."


class TestConfirmListSharedWithUser:
    def test_confirm_list_shared_with_user(self, example_response):
        cognito_user_id = '12345678-user-0002-1234-abcdefghijkl'
        list_id = '12345678-list-0002-1234-abcdefghijkl'
        result = common.confirm_list_shared_with_user(cognito_user_id, list_id, example_response)
        assert result, "List should be shared with user."

    def test_confirm_list_not_shared_with_user(self, example_response):
        cognito_user_id = 'eu-west-1:dc7b5ba3-835f-4859-ae67-06af31c2ce03'
        list_id = '12345678-list-0002-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            common.confirm_list_shared_with_user(cognito_user_id, list_id, example_response)
        assert str(e.value) == "List ID 12345678-list-0002-1234-abcdefghijkl did not have a shared item with user eu-west-1:dc7b5ba3-835f-4859-ae67-06af31c2ce03.", "Exception not thrown for list not being shared with user."


class TestGenerateListObject:
    def test_generate_list_object(self, example_response):
        items = common.generate_list_object(example_response)
        assert items['list']['listId'] == "12345678-list-0002-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert items['list']['title'] == "Oscar's 1st Birthday", "Get list response did not contain a title."
        assert items['list']['description'] == "A gift list for Oscars birthday.", "Get list response did not contain a description."
        assert items['list']['occasion'] == "Birthday", "Get list response did not contain an occasion."

        assert len(items['products']) == 2, "Number of products was not 2."

        assert items['products'][0]['productId'] == "12345678-prod-0001-1234-abcdefghijkl", "Product ID was not correct."
        assert items['products'][0]['quantity'] == 1, "Quantity of product was not correct."
        assert items['products'][0]['reserved'] == 0, "Reserved quantity of product was not correct."
        assert items['products'][0]['type'] == 'products', "Type of product was not correct."

        assert items['products'][1]['productId'] == "12345678-prod-0002-1234-abcdefghijkl", "Product ID was not correct."
        assert items['products'][1]['quantity'] == 2, "Quantity of product was not correct."
        assert items['products'][1]['reserved'] == 1, "Reserved quantity of product was not correct."
        assert items['products'][1]['type'] == 'notfound', "Type of product was not correct."
        reservedDetails = items['products'][1]['reservedDetails']
        assert len(reservedDetails) == 1, "Reserved details of product was not correct."
        assert reservedDetails[0]['name'] == 'Test User', "Reserved details name is not as expected."
