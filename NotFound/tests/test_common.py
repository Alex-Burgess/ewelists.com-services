import pytest
import os
import re
from notfound import common
import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture()
def api_gateway_with_id_event():
    """ Generates API GW Event"""

    return {
      "resource": "/notfound/{id}",
      "path": "/notfound/12345678-list-0001-1234-abcdefghijkl",
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
          "resourcePath": "/notfound/{id}",
          "httpMethod": "GET",
          "extendedRequestId": "BMsiDFARjoEFgOg=",
          "requestTime": "07/Oct/2019:15:33:45 +0000",
          "path": "/test/notfound/12345678-list-0001-1234-abcdefghijkl",
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
def api_gateway_postman_event():
    """ Generates API GW Event"""

    return {
      "resource": "/notfound/{id}",
      "path": "/notfound/12345678-list-0001-1234-abcdefghijkl",
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
          "resourcePath": "/notfound/{id}",
          "httpMethod": "GET",
          "extendedRequestId": "BMsiDFARjoEFgOg=",
          "requestTime": "07/Oct/2019:15:33:45 +0000",
          "path": "/test/notfound/12345678-list-0001-1234-abcdefghijkl",
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
      "resource": "/notfound/{id}",
      "path": "/notfound/12345678-list-0001-1234-abcdefghijkl",
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
          "resourcePath": "/notfound/{id}",
          "httpMethod": "GET",
          "extendedRequestId": "BMsiDFARjoEFgOg=",
          "requestTime": "07/Oct/2019:15:33:45 +0000",
          "path": "/test/notfound/12345678-list-0001-1234-abcdefghijkl",
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


@pytest.fixture()
def api_gateway_event_with_no_product_id():
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
        "body": "null",
        "isBase64Encoded": "false"
    }


def test_create_response():
    response = common.create_response(200, 'Success message')

    expected_response = {'statusCode': 200,
                         'body': 'Success message',
                         'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                         }}
    assert response == expected_response, "Create_response did not return the expected response value."


class TestGetPostmanIdentity:
    def test_get_postman_identity(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_IDENTITY_ID', 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl')
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')

        identity = common.get_postman_identity(os.environ, 1)
        assert identity['POSTMAN_IDENTITY_ID'] == 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl', "POSTMAN_IDENTITY_ID not as expected."
        assert identity['POSTMAN_USERPOOL_SUB'] == '12345678-user-api1-1234-abcdefghijkl', "POSTMAN_USERPOOL_SUB not as expected."

    def test_get_postman_identity2(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_IDENTITY_ID2', 'eu-west-1:12345678-user-fed2-1234-abcdefghijkl')
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB2', '12345678-user-api2-1234-abcdefghijkl')

        identity = common.get_postman_identity(os.environ, 2)
        assert identity['POSTMAN_IDENTITY_ID'] == 'eu-west-1:12345678-user-fed2-1234-abcdefghijkl', "POSTMAN_IDENTITY_ID not as expected."
        assert identity['POSTMAN_USERPOOL_SUB'] == '12345678-user-api2-1234-abcdefghijkl', "POSTMAN_USERPOOL_SUB not as expected."

    def test_get_postman_identity_when_both_osvars_missing(self):
        with pytest.raises(Exception) as e:
            common.get_postman_identity(os.environ, 1)
        assert str(e.value) == "POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."

    def test_get_postman_identity_when_userpool_missing(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_IDENTITY_ID', 'eu-west-1:12345678-user-fed1-1234-abcdefghijkl')
        with pytest.raises(Exception) as e:
            common.get_postman_identity(os.environ, 1)
        assert str(e.value) == "POSTMAN_IDENTITY_ID and POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."

    def test_get_postman_identity_when_identity_id_missing(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')
        with pytest.raises(Exception) as e:
            common.get_postman_identity(os.environ, 1)
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

    def test_get_identity_when_postman2_request(self, monkeypatch, api_gateway_postman_event):
        api_gateway_postman_event['requestContext']['identity']['userArn'] = "arn:aws:iam::123456789012:user/ApiTestUser2"
        monkeypatch.setitem(os.environ, 'POSTMAN_IDENTITY_ID2', 'eu-west-1:12345678-user-fed2-1234-abcdefghijkl')
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB2', '12345678-user-api2-1234-abcdefghijkl')
        identity = common.get_identity(api_gateway_postman_event, os.environ)
        assert identity["cognitoIdentityId"] == "eu-west-1:12345678-user-fed2-1234-abcdefghijkl", "cognitoIdentityId not as expected."
        assert identity["userPoolSub"] == "12345678-user-api2-1234-abcdefghijkl", "userPoolSub not as expected."

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
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'notfound-test')
        table_name = common.get_table_name(os.environ)
        assert table_name == "notfound-test", "Table name from os environment variables was not as expected."

    def test_get_table_name_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common.get_table_name(os.environ)
        assert str(e.value) == "TABLE_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetProductId:
    def test_get_product_id(self, api_gateway_with_id_event):
        product_id = common.get_product_id(api_gateway_with_id_event)
        assert product_id == "12345678-list-0001-1234-abcdefghijkl", "Product ID returned from API event was not as expected."

    def test_product_id_not_present(self, api_gateway_event_with_no_product_id):
        with pytest.raises(Exception) as e:
            common.get_product_id(api_gateway_event_with_no_product_id)
        assert str(e.value) == "API Event did not contain a Product ID in the path parameters.", "Exception not as expected."
