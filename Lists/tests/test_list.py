import pytest
import os
import re
import json
import boto3
from moto import mock_dynamodb2
from lists import list

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def api_gateway_listall_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists",
        "path": "/lists/",
        "httpMethod": "GET",
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "no-cache",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "false",
            "CloudFront-Is-Mobile-Viewer": "true",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "GB",
            "content-type": "application/x-www-form-urlencoded",
            "Host": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "origin": "http://localhost:3000",
            "pragma": "no-cache",
            "Referer": "http://localhost:3000/",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Mobile Safari/537.36",
            "Via": "2.0 5f8ce6fad85064c6a8d3486ad2c8e170.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "Eohcm5xlRayoVmO49AJOQS-1PBFSbLdPBT76JPTRWiAkHenB39WxwA==",
            "x-amz-date": "20191003T101607Z",
            "x-amz-security-token": "AgoJb3JpZ2luX2VjECoaCWV1LXdlc3QtMSJGMEQCIBiEv5QsTdXMr9UDmSsNs6heGHDhdqiZy0F995DDDbOfAiBgSnJJXIEKkAyS3KLqUNmuYqYrd1JXrzUnd8HKW0NKYCqmBQgTEAAaDDY2MTc5MjE4Njk2NyIM72PFfjza89L2YYq4KoMFuyociqlW6d5GiRrGsZrjGokiKKhJOu5Jw9V0sucAENKFgZ6Rzh5e17m0dolVQ1tIUYV72LEhtqQwivkzt40dUlIkfL6Mlf78iABzZEACOKzq7EN82osFxl9kqCu74b7E+A/Pifo2dWpiwLS+MaZS6FtbsGL5Oq6LGa0NF+T/doRdqbVjhCC2M5odaFG/ujosWihUvckhNa0j/QS90UdQgIrzSYQV79H9RExtTzLX/u4lt4LuCl4TY3MFnwHTk0HnaRHS+9g2XzyFyjplVq66G9dCGJN1X/fMTq/T1BgBn9jvaeKgNY4hQyK+yfypOTbY1SUMTT31tvJiHecjzXOQWcD+Uvnx2x+6Q9kK4Ad8121N4qQ2ZBMjMi4dlPqzDV5XhE9eLPQe2koeadsK1B8QdyyFNn0K0tt9Ewtg9ugbrzSlCIjvcT+BrmyyPpAp6oLeMQCvbsY9gJm6e06l9MwOe7BpNMFPgVW7qE9P3cAgXuqQEL0F9SMqn7LP9HbUFTbV9diufGhYu2ojSoOOJNmmMv1WIhuteTfz6Xab+cNrBAHCc24EZn9uYQwO0o5oNnyvM9XaVrYJSRKhhh8ffSiO63s3sohsy9Mjlpg331Q/wYeP03JOr9As9nowOGt1mDHN3I8Onsnzy8QocsK9vuRhGYnTFcaUxkkaVXrVs4R9sWWMVPBdmlH5j4uCbj7Bhz9ue2vYIPJKitf3ImycrHruyKBFdcuwWoUad+6NqH5IGTHGlNQ+8Wf/85dfSOXuzc8bio/pxY5pC7RhYMbH9snboXdanJRrJGuNIyMWW6kpMrlWXf/X/ZCsGGQNsKAxV55RmMR/Ppx3rwumgqtk1/SxI05qSjC7ktfsBTq1AVs+Xn7AU0Zr86d1MaDvYOA+PGGc0zzv7Xfy8R+tCw3lBUzdgTVKOU3wISCznw/eEv9xVEU5A7crYH0K9VnkTzDH1WzNFZ2FiYyZZfTY2aD6Y7gqK5pLjmSZqQzDWOCkoKG8cGU7Zh/N/ip82g6wTzW0TJBoY+cr3w1Rzy+v8AWS8Z/JPmxWSRZFPW2RNdf9Mww9cr/9DB+YO+HZ2HHdkWLQazVBqbGF3pCpTRFYRhBI8K4cuPc=",
            "X-Amzn-Trace-Id": "Root=1-5d95ca67-d4538cd8541a09a03641f6e8",
            "X-Forwarded-For": "31.49.230.217, 130.176.6.159",
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
            "httpMethod": "GET",
            "extendedRequestId": "A-yQJG9qjoEF8ug=",
            "requestTime": "03/Oct/2019:10:16:07 +0000",
            "path": "/test/lists/",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "test",
            "domainPrefix": "4sdcvv0n2e",
            "requestTimeEpoch": 1570097767237,
            "requestId": "377d5056-a813-4c75-9c9a-1a0c59a25e03",
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
                },
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            },
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'userId-index',
                    'KeySchema': [
                         {
                             'AttributeName': 'userId',
                             'KeyType': 'HASH'
                         },
                         {
                             'AttributeName': 'PK',
                             'KeyType': 'RANGE'
                         }
                     ],
                     'Projection': {
                        'ProjectionType': 'ALL'
                     }
                }
            ]
        )

    items = [
        {"PK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "SK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "email": "test.user@gmail.com", "name": "Test User", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c"},
        {"PK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684", "SK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684", "email": "test.user2@gmail.com", "name": "Test User2", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684"},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-abcd-abcd-123456789112", "createdAt": "2018-09-01T10:00:00", "listOwner": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "description": "A gift list for Api Childs birthday.", "eventDate": "2019-09-01"},
        {"PK": "LIST#12345678-abcd-abcd-123456789112", "SK": "SHARE#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "listId": "12345678-abcd-abcd-123456789112", "createdAt": "2018-09-01T10:00:00", "listOwner": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "description": "A gift list for Api Childs birthday.", "eventDate": "2019-09-01"},
        {"PK": "LIST#12345678-efgh-efgh-123456789112", "SK": "SHARE#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "listId": "12345678-efgh-efgh-123456789112", "createdAt": "2018-09-01T10:00:00", "listOwner": "eu-west-1:1234250a-0fb0-4b32-9842-041c69be1234", "description": "A gift list for Oscars birthday.", "eventDate": "2018-10-31"},
        {"PK": "LIST#87654321-axyz-axyz-123456789112", "SK": "SHARE#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "title": "Oscar's 2nd Birthday", "occasion": "Birthday", "listId": "87654321-axyz-axyz-123456789112", "createdAt": "2019-09-01T10:00:00", "listOwner": "eu-west-1:6789250a-0fb0-4b32-9842-041c69be6789", "description": "A gift list for Oscars 2nd Birthday.", "eventDate": "2019-10-31"}
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetLists:
    def test_get_lists(self, dynamodb_mock):
        cognito_identity_id = 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'
        lists_response = list.get_lists('lists-unittest', 'userId-index', cognito_identity_id)

        test_user = {"email": "test.user@gmail.com", "name": "Test User"}
        assert lists_response['user'] == test_user, "Test user was not as expected."

        owned_list = {"listId": "12345678-abcd-abcd-123456789112", "title": "Api Child's 1st Birthday", "occasion": "Birthday", "description": "A gift list for Api Childs birthday."}
        assert len(lists_response['owned']) == 1, "User should only own 1 list."
        assert lists_response['owned'][0] == owned_list, "Details of the list owned by user was not as expected."

        shared_list1 = {"listId": "12345678-efgh-efgh-123456789112", "title": "Oscar's 1st Birthday", "occasion": "Birthday", "description": "A gift list for Oscars birthday."}
        shared_list2 = {"listId": "87654321-axyz-axyz-123456789112", "title": "Oscar's 2nd Birthday", "occasion": "Birthday", "description": "A gift list for Oscars 2nd Birthday."}
        assert len(lists_response['shared']) == 2, "User should only have 2 lists shared with them."
        assert lists_response['shared'][0] == shared_list1, "Details of the list shared with user was not as expected."
        assert lists_response['shared'][1] == shared_list2, "Details of the list shared with user was not as expected."

    def test_get_lists_bad_table_name(self, dynamodb_mock):
        cognito_identity_id = 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'

        with pytest.raises(Exception) as e:
            list.get_lists('lists-unittes', 'userId-index', cognito_identity_id)
        assert str(e.value) == "Unexpected error when getting lists from table.", "Exception not as expected."

    def test_get_lists_bad_index_name(self, dynamodb_mock):
        cognito_identity_id = 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c'

        with pytest.raises(Exception) as e:
            list.get_lists('lists-unittest', 'userId-inde', cognito_identity_id)
        assert str(e.value) == "Unexpected error when getting lists from table.", "Exception not as expected."

    def test_get_lists_for_user_with_no_lists(self, dynamodb_mock):
        cognito_identity_id = 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684'
        lists_response = list.get_lists('lists-unittest', 'userId-index', cognito_identity_id)
        assert len(lists_response['owned']) == 0, "Number of lists was not 0."
        assert len(lists_response['shared']) == 0, "Number of lists was not 0."


class TestListMain:
    def test_list_main(self, api_gateway_listall_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        response = list.list_main(api_gateway_listall_event)
        body = json.loads(response['body'])

        assert len(body['owned']) == 1, "Number of lists returned was not as expected."
        assert len(body['shared']) == 2, "Number of lists returned was not as expected."

    def test_list_main_no_table(self, api_gateway_listall_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')
        response = list.list_main(api_gateway_listall_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting lists from table.', "Exception was not as expected."

    def test_list_main_no_lists(self, api_gateway_listall_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_listall_event['requestContext']['identity']['cognitoIdentityId'] = 'eu-west-1:db9476fd-de77-4977-839f-4f943ff5d684'
        response = list.list_main(api_gateway_listall_event)
        body = json.loads(response['body'])

        assert len(body['owned']) == 0, "Number of lists returned was not as expected."
        assert len(body['shared']) == 0, "Number of lists returned was not as expected."


def test_handler(api_gateway_listall_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = list.handler(api_gateway_listall_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"user": .*}', response['body'])
