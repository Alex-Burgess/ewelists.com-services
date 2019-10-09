import pytest
import os
import re
import json
import copy
import boto3
from moto import mock_dynamodb2
from lists import delete

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_delete_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists/{id}",
        "path": "/lists/1234abcd",
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
            "Host": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "Postman-Token": "14108774-338e-40b0-a144-1cd572d7300a",
            "User-Agent": "PostmanRuntime/7.15.2",
            "Via": "1.1 0b087ba0ae8ddae6c31ec71886481983.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "JjtwdkuUrtV3PuN3LKq94JDN_iw2SxVgLUq9nGRvxpTmyJtK4r-ANQ==",
            "x-amz-date": "20191007T100020Z",
            "X-Amzn-Trace-Id": "Root=1-5d9b0cb5-31fa3dbc22f4a1524217419e",
            "X-Forwarded-For": "5.81.150.55, 70.132.38.80",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "queryStringParameters": "null",
        "multiValueQueryStringParameters": "null",
        "pathParameters": {
            "id": "1234abcd"
        },
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "4j13uq",
            "resourcePath": "/lists/{id}",
            "httpMethod": "DELETE",
            "extendedRequestId": "BL7sTFalDoEFrYA=",
            "requestTime": "07/Oct/2019:10:00:21 +0000",
            "path": "/test/lists/1234abcd",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "test",
            "domainPrefix": "4sdcvv0n2e",
            "requestTimeEpoch": 1570442421085,
            "requestId": "8e707954-1ef5-492c-b88e-35f74f4e21de",
            "identity": {
                "cognitoIdentityPoolId": "eu-west-1:2208d797-dfc9-40b4-8029-827c9e76e029",
                "accountId": "123456789012",
                "cognitoIdentityId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c",
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
                    'AttributeName': 'userId',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'listId',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'listId',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

    item = {
        'userId': 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c',
        'userPoolSub': '42cf26f5-407c-47cf-bcb6-f70cd63ac119',
        'listId': '1234abcd',
        'title': 'My Test List',
        'description': 'Test description for the list.',
        'occasion': 'Birthday',
        'createdAt': 1570552083
    }

    table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestDeleteItem:
    def test_delete_item(self, dynamodb_mock):
        cognito_identity_id = 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'
        list_id = '1234abcd'
        message = delete.delete_item('lists-unittest', cognito_identity_id, list_id)
        assert message == 'Delete request successfull for List ID: 1234abcd and user: eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c.', "Delete message was not as expected."

    @pytest.mark.skip(reason="Moto is not throwing an exception when deleting with ConditionExpression")
    def test_delete_item_no_list(self, dynamodb_mock):
        cognito_identity_id = 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'
        list_id = '1234abce'

        with pytest.raises(Exception) as e:
            delete.delete_item('lists-unittest', cognito_identity_id, list_id)
        assert str(e.value) == "List does not exist.", "Exception not as expected."


class TestDeleteMain:
    def test_delete_main(self, api_gateway_delete_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = delete.delete_main(api_gateway_delete_event)
        body = json.loads(response['body'])

        assert body['deleted'], "Delete main response did not contain the correct status."
        assert len(body['listId']) == 8, "Create main response did not contain a listId."
        assert body['message'] == 'Delete request successfull for List ID: 1234abcd and user: eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c.', "Delete main response did not contain the correct message."

    def test_delete_main_with_bad_table_name(self, api_gateway_delete_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = delete.delete_main(api_gateway_delete_event)
        body = json.loads(response['body'])
        assert body['error'] == 'List does not exist.', "Create main response did not contain the correct error message."


def test_handler(api_gateway_delete_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = delete.handler(api_gateway_delete_event, None)
    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    assert re.match('{"deleted": .*}', response['body']), "Response body was not as expected."
