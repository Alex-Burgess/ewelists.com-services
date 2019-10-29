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
        "path": "/lists/12345678-list-0001-1234-abcdefghijkl",
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
            "id": "12345678-list-0001-1234-abcdefghijkl"
        },
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/lists/{id}",
            "httpMethod": "PUT",
            "extendedRequestId": "BQGojGkBjoEFsTw=",
            "requestTime": "08/Oct/2019:16:22:40 +0000",
            "path": "/test/lists/12345678-list-0001-1234-abcdefghijkl",
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
                    'AttributeName': 'PK',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'SK',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'PK',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'SK',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

    # 2 users. User 1 owns list 1, which is shared with user 2 and a pending user 3 which has not signed up yet.
    items = [
        {"PK": "USER#12345678-user-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "email": "test.user@gmail.com", "name": "Test User", "userId": "12345678-user-0001-1234-abcdefghijkl"},
        {"PK": "USER#12345678-user-0002-1234-abcdefghijkl", "SK": "USER#12345678-user-0002-1234-abcdefghijkl", "email": "test.user2@gmail.com", "name": "Test User2", "userId": "12345678-user-0002-1234-abcdefghijkl"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "description": "A gift list for Oscars birthday.", "eventDate": "2018-10-31"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "userId": "12345678-user-0001-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "description": "A gift list for Oscars birthday.", "eventDate": "2018-10-31"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "description": "A gift list for Oscars birthday.", "eventDate": "2018-10-31"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PENDING#test.user3@gmail.com", "email": "test.user3@gmail.com", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": "2018-09-01T10:00:00", "description": "A gift list for Oscars birthday.", "eventDate": "2018-10-31"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1009", "quantity": 1, "reserved": 0},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PRODUCT#1010", "quantity": 2, "reserved": 1, "reservedDetails": {"userId": "12345678-user-0002-1234-abcdefghijkl", "name": "Test User2", "reserved": 1, "timestamp": "2018-11-01T10:00:00"}}
    ]

    for item in items:
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


class TestGetItemsToUpdate:
    def test_get_items_to_update(self, dynamodb_mock):
        items = update.get_items_to_update('lists-unittest', '12345678-list-0001-1234-abcdefghijkl')
        assert len(items) == 4
        assert items[0]['SK']['S'] == 'PENDING#test.user3@gmail.com'
        assert items[1]['SK']['S'] == 'SHARE#12345678-user-0001-1234-abcdefghijkl'
        assert items[2]['SK']['S'] == 'SHARE#12345678-user-0002-1234-abcdefghijkl'
        assert items[3]['SK']['S'] == 'USER#12345678-user-0001-1234-abcdefghijkl'


class TestUpdateList:
    def test_update_list_with_one_attribute(self, api_gateway_update_event, dynamodb_mock):
        api_gateway_update_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"A gift list for Oscars birthday.\",\n    \"occasion\": \"Birthday\"\n}"
        update_attributes = json.loads(api_gateway_update_event['body'])
        items = [
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'SHARE#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Oscar's 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Oscars birthday.'}, 'eventDate': {'S': '2018-10-31'}},
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Oscar's 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Oscars birthday.'}, 'eventDate': {'S': '2018-10-31'}}
        ]

        updates = update.update_list('lists-unittest', items, update_attributes)

        assert len(updates) == 2, "Update response did not contain expected number of updated attributes."
        assert updates[0]['SK'] == 'SHARE#12345678-user-0001-1234-abcdefghijkl'
        assert updates[0]['updates'] == {'title': 'My Updated Title'}
        assert updates[1]['SK'] == 'USER#12345678-user-0001-1234-abcdefghijkl'
        assert updates[1]['updates'] == {'title': 'My Updated Title'}

    def test_update_list_with_multiple_attributes(self, api_gateway_update_event, dynamodb_mock):
        api_gateway_update_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"Updated.\",\n    \"occasion\": \"Christmas\"\n}"
        update_attributes = json.loads(api_gateway_update_event['body'])
        items = [
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'SHARE#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Oscar's 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Oscars birthday.'}, 'eventDate': {'S': '2018-10-31'}},
            {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Oscar's 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Oscars birthday.'}, 'eventDate': {'S': '2018-10-31'}}
        ]

        updates = update.update_list('lists-unittest', items, update_attributes)

        assert len(updates) == 2, "Update response did not contain expected number of updated attributes."
        assert updates[0]['SK'] == 'SHARE#12345678-user-0001-1234-abcdefghijkl'
        assert updates[0]['updates'] == {'title': 'My Updated Title', 'description': 'Updated.', 'occasion': 'Christmas'}
        assert updates[1]['SK'] == 'USER#12345678-user-0001-1234-abcdefghijkl'
        assert updates[1]['updates'] == {'title': 'My Updated Title', 'description': 'Updated.', 'occasion': 'Christmas'}


class TestUpdateListMain:
    def test_update_list_main_with_just_title(self, api_gateway_update_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_update_event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"A gift list for Oscars birthday.\",\n    \"occasion\": \"Birthday\"\n}"
        response = update.update_list_main(api_gateway_update_event)
        body = json.loads(response['body'])

        expected_body = [
            {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PENDING#test.user3@gmail.com", "updates": {"title": "My Updated Title"}},
            {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "updates": {"title": "My Updated Title"}},
            {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "updates": {"title": "My Updated Title"}},
            {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "updates": {"title": "My Updated Title"}}
        ]

        assert len(body) == 4, "Update main response did not contain expected number of updated items."
        assert body == expected_body, "Updates from response were not as expected."

    def test_update_list_main_with_empty_body(self, monkeypatch, api_gateway_update_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_update_event['body'] = "null"
        response = update.update_list_main(api_gateway_update_event)
        body = json.loads(response['body'])
        assert body['error'] == 'API Event Body was empty.', "Update main response did not contain the correct error message."

    def test_update_list_that_does_not_exist(self, monkeypatch, api_gateway_update_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_update_event['pathParameters']['id'] = "12345678-list-0009-1234-abcdefghijkl"

        response = update.update_list_main(api_gateway_update_event)
        body = json.loads(response['body'])
        assert body['error'] == 'No list exists with this ID.', "Update main response did not contain the correct error message."

    def test_update_list_with_bad_table(self, monkeypatch, api_gateway_update_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')
        api_gateway_update_event['pathParameters']['id'] = "12345678-list-0009-1234-abcdefghijkl"

        response = update.update_list_main(api_gateway_update_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Unexpected error when getting lists from table.', "Update main response did not contain the correct error message."

    def test_update_list_with_requestor_not_owner(self, monkeypatch, api_gateway_update_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_update_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0002-1234-abcdefghijkl"

        response = update.update_list_main(api_gateway_update_event)
        body = json.loads(response['body'])
        assert body['error'] == 'Owner of List ID 12345678-list-0001-1234-abcdefghijkl did not match user id of requestor: 12345678-user-0002-1234-abcdefghijkl.', "Update main response did not contain the correct error message."


def test_handler(api_gateway_update_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = update.handler(api_gateway_update_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    expected_body = [
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PENDING#test.user3@gmail.com", "updates": {"title": "My Updated Title", "occasion": "Christmas", "description": "Updated description for the list."}},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0001-1234-abcdefghijkl", "updates": {"title": "My Updated Title", "occasion": "Christmas", "description": "Updated description for the list."}},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "SHARE#12345678-user-0002-1234-abcdefghijkl", "updates": {"title": "My Updated Title", "occasion": "Christmas", "description": "Updated description for the list."}},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "updates": {"title": "My Updated Title", "occasion": "Christmas", "description": "Updated description for the list."}}
    ]

    assert body == expected_body
