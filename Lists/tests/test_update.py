import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import update

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_update_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists/{id}",
        "path": "/lists/1234abcd",
        "httpMethod": "PUT",
        "body": "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"Updated description for the list.\",\n    \"occasion\": \"Christmas\"\n}",
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
            "Postman-Token": "d38bfa3c-26b3-4a42-acfa-ecc30a12d767",
            "User-Agent": "PostmanRuntime/7.15.2",
            "Via": "1.1 f76142b838785e2eec49408a3d9d8285.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "pUhW1u14GSPTlHCQed4C5eTsM3Biv_ca3cDVCh9hbcnZ3_e4z0CgVw==",
            "x-amz-content-sha256": "51f3f8790f9b06462165164ab5e1bf33fd64f8230e962c445681a63555e04429",
            "x-amz-date": "20191007T160043Z",
            "X-Amzn-Trace-Id": "Root=1-5d9b612b-c2a6fbd0452771f0b0155f70",
            "X-Forwarded-For": "5.81.150.55, 70.132.15.71",
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
            "httpMethod": "PUT",
            "extendedRequestId": "BMwexGf4DoEFoJA=",
            "requestTime": "07/Oct/2019:16:00:43 +0000",
            "path": "/test/lists/1234abcd",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "test",
            "domainPrefix": "4sdcvv0n2e",
            "requestTimeEpoch": 1570464043231,
            "requestId": "c410dfa4-713a-4ac3-afe5-2e3ab3d4066f",
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


class TestGetAttributeDetails:
    def test_get_attribute_details_with_correct_attributes(self, api_gateway_update_event):
        update_attributes = update.get_attribute_details(api_gateway_update_event)

        assert len(update_attributes) == 3, "Update attributes object did not contain expected number of attributes."
        assert update_attributes['title'] == "My Updated Title", "Update attributes object did not contain title as expected."
        assert update_attributes['description'] == "Updated description for the list.", "Update attributes object did not contain description as expected."
        assert update_attributes['occasion'] == "Christmas", "Update attributes object did not contain occasion as expected."

    def test_get_attribute_details_with_one_attributes(self, api_gateway_update_event):
        api_gateway_update_event['body'] = "{\n    \"title\": \"My Updated Title\"\n}"

        with pytest.raises(Exception) as e:
            update.get_attribute_details(api_gateway_update_event)
        assert str(e.value) == "Event body did not contain the expected keys ['title', 'description', 'occasion'].", "Exception not as expected."

    def test_get_attribute_details_with_empty_body(self, api_gateway_update_event):
        api_gateway_update_event['body'] = "null"

        with pytest.raises(Exception) as e:
            update.get_attribute_details(api_gateway_update_event)
        assert str(e.value) == "API Event Body was empty.", "Exception not as expected."

    def test_get_attribute_details_with_body_not_json(self, api_gateway_update_event):
        api_gateway_update_event['body'] = "some text"

        with pytest.raises(Exception) as e:
            update.get_attribute_details(api_gateway_update_event)
        assert str(e.value) == "API Event did not contain a valid body.", "Exception not as expected."


class TestUpdateList:
    def test_update_list_with_one_attribute(self, api_gateway_update_event, dynamodb_mock):
        cognito_identity_id = "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c"
        list_id = "1234abcd"
        api_gateway_update_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"Test description for the list.\",\n    \"occasion\": \"Birthday\"\n}"

        update_attributes = json.loads(api_gateway_update_event['body'])
        response = update.update_list('lists-unittest', cognito_identity_id, list_id, update_attributes)

        assert len(response) == 1, "Update response did not contain expected number of updated attributes."
        assert response['title']['S'] == "My Updated Title", "Update response did not contain expected value for title."

    def test_update_list_with_wrong_table(self, api_gateway_update_event, dynamodb_mock):
        cognito_identity_id = "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c"
        list_id = "1234abcd"
        api_gateway_update_event['body'] = "{\n    \"title\": \"My Updated Title\"\n}"
        update_attributes = json.loads(api_gateway_update_event['body'])

        with pytest.raises(Exception) as e:
            update.update_list('lists-unittet', cognito_identity_id, list_id, update_attributes)
        assert str(e.value) == "Unexpected error when updating the list item.", "Exception not as expected."

    def test_update_list_with_multiple_attributes(self, api_gateway_update_event, dynamodb_mock):
        cognito_identity_id = "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c"
        list_id = "1234abcd"
        update_attributes = json.loads(api_gateway_update_event['body'])
        response = update.update_list('lists-unittest', cognito_identity_id, list_id, update_attributes)

        assert len(response) == 3, "Update response did not contain expected number of updated attributes."
        assert response['title']['S'] == "My Updated Title", "Update response did not contain expected value for title."


class TestUpdateListMain:
    def test_update_list_main(self, api_gateway_update_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = update.update_list_main(api_gateway_update_event)
        body = json.loads(response['body'])

        expected_body = {"title": {"S": "My Updated Title"}, "description": {"S": "Updated description for the list."}, "occasion": {"S": "Christmas"}}

        assert len(body.keys()) == 3, "Update main response did not contain expected number of updated attributes."
        assert body == expected_body, "Updated attributes from response were not as expected."

    def test_update_list_main_with_just_title(self, api_gateway_update_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_update_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"Test description for the list.\",\n    \"occasion\": \"Birthday\"\n}"
        response = update.update_list_main(api_gateway_update_event)
        body = json.loads(response['body'])

        expected_body = {"title": {"S": "My Updated Title"}}

        assert len(body.keys()) == 1, "Update main response did not contain expected number of updated attributes."
        assert body == expected_body, "Updated attributes from response were not as expected."

    def test_update_list_main_with_empty_body(self, monkeypatch, api_gateway_update_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_update_event['body'] = "null"
        response = update.update_list_main(api_gateway_update_event)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event Body was empty.', "Update main response did not contain the correct error message."


def test_handler(api_gateway_update_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = update.handler(api_gateway_update_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"title": .*}', response['body'])
