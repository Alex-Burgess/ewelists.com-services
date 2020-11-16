import json
import os
import pytest
import boto3
import uuid
from moto import mock_dynamodb2, mock_cognitoidp


@pytest.fixture
def cognito_mock():
    with mock_cognitoidp():
        client = boto3.client('cognito-idp', region_name='eu-west-1')

        user_pool_id = client.create_user_pool(PoolName='ewelists-unittest')["UserPool"]["Id"]
        print("Userpool ID: " + user_pool_id)

        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=str(uuid.uuid4()),
            UserAttributes=[{"Name": "email", "Value": 'test.exists@gmail.com'}]
        )

        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=str(uuid.uuid4()),
            UserAttributes=[{"Name": "email", "Value": 'test.exists2@googlemail.com'}]
        )

        yield


@pytest.fixture
def user_pool_id(monkeypatch):
    client = boto3.client('cognito-idp', region_name='eu-west-1')
    list_response = client.list_user_pools(MaxResults=1)
    id = list_response['UserPools'][0]['Id']
    return id


@pytest.fixture
def dynamodb_mock():
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        table = dynamodb.create_table(
            TableName='lists-unittest',
            KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}, {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'},
                {'AttributeName': 'reservationId', 'AttributeType': 'S'},
                {'AttributeName': 'userId', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'email-index',
                    'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'userId-index',
                    'KeySchema': [{'AttributeName': 'userId', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'SK-index',
                    'KeySchema': [{'AttributeName': 'SK', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                },
                {
                    'IndexName': 'reservationId-index',
                    'KeySchema': [{'AttributeName': 'reservationId', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )

        items = load_test_data()

        for item in items:
            table.put_item(TableName='lists-unittest', Item=item)

        yield


def load_test_data():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, './data.json')

    items = []
    with open(filename, 'r') as f:
        for row in f:
            items.append(json.loads(row))
    return items


def api_event():
    """ Generates API GW Event"""

    return {
        "resource": "/lists",
        "path": "/lists",
        "httpMethod": "GET",
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/lists",
            "httpMethod": "GET",
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
        "body": None,
        "isBase64Encoded": "false"
    }


def api_event_no_auth():
    """ Generates API GW Event"""

    return {
        "resource": "/lists",
        "path": "/lists",
        "httpMethod": "GET",
        "queryStringParameters": None,
        "multiValueQueryStringParameters": None,
        "pathParameters": None,
        "stageVariables": None,
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/lists",
            "httpMethod": "GET",
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
                "cognitoIdentityPoolId": None,
                "accountId": None,
                "cognitoIdentityId": None,
                "caller": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials",
                "sourceIp": "31.49.230.217",
                "principalOrgId": "o-d8jj6dyqv2",
                "accessKey": None,
                "cognitoAuthenticationType": None,
                "cognitoAuthenticationProvider": None,
                "userArn": None,
                "userAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Mobile Safari/537.36",
                "user": None
            },
            "domainName": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "apiId": "4sdcvv0n2e"
        },
        "body": None,
        "isBase64Encoded": "false"
    }


@pytest.fixture
def api_base_event():
    return api_event()


@pytest.fixture
def api_no_auth_base_event():
    return api_event_no_auth()


@pytest.fixture
def api_postman_event():
    event = api_event()
    event['requestContext']['identity'] = {
        "cognitoIdentityPoolId": None,
        "accountId": "123456789012",
        "cognitoIdentityId": None,
        "caller": "ABCDEFGPDMJL4EB35H6H",
        "sourceIp": "5.81.150.55",
        "principalOrgId": "o-d8jj6dyqv2",
        "accessKey": "ABCDEFGPDMJL4EB35H6H",
        "cognitoAuthenticationType": None,
        "cognitoAuthenticationProvider": None,
        "userArn": "arn:aws:iam::123456789012:user/ApiTestUser",
        "userAgent": "PostmanRuntime/7.15.2",
        "user": "ABCDEFGPDMJL4EB35H6H"
    }

    return event


@pytest.fixture
def api_create_event():
    event = api_event()
    event['httpMethod'] = "POST"
    event['body'] = json.dumps({
        "title": "My Birthday List",
        "description": "A gift wish list for my birthday.",
        "eventDate": "25 December 2020",
        "occasion": "Birthday",
        "imageUrl": "/images/celebration-default.jpg",
    })

    return event


@pytest.fixture
def api_add_product_event():
    event = api_event()
    event['resource'] = "/lists/{id}/product/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0100-1234-abcdefghijkl"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0100-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"quantity\": 1,\n    \"productType\": \"products\"\n}"

    return event


@pytest.fixture
def api_delete_product_event():
    event = api_event()
    event['resource'] = "/lists/{id}/product/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"productType\": \"products\"\n}"

    return event


@pytest.fixture
def api_gateway_get_list_event():
    event = api_event()
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl",
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = None

    return event


@pytest.fixture
def api_get_shared_list_event():
    event = api_event()
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl",
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = None

    return event


@pytest.fixture
def api_get_shared_list_unauthed_event():
    event = api_event_no_auth()
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl",
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = None

    return event


@pytest.fixture
def api_list_event():
    event = api_event()
    event['resource'] = "/lists/"
    event['path'] = "/lists",
    event['httpMethod'] = "GET"

    return event


@pytest.fixture
def api_close_event():
    event = api_event()
    event['resource'] = "/lists/{id}/close"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl",
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = None

    return event


@pytest.fixture
def api_delete_event():
    event = api_event()
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}

    return event


@pytest.fixture
def api_purchase_event():
    event = api_event_no_auth()
    event['httpMethod'] = "POST"
    event['resource'] = "/lists/purchase/{reservationid}/email/{email}"
    event['path'] = "/lists/purchase/12345678-resv-0001-1234-abcdefghijkl/email/test.user2@gmail.com"
    event['pathParameters'] = {"reservationid": "12345678-resv-0001-1234-abcdefghijkl", "email": "test.user2@gmail.com"}
    event['body'] = json.dumps({
        "product": {
            "type": "products",
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "productUrl": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "imageUrl": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }
    })

    return event


@pytest.fixture
def api_reservation_event():
    event = api_event_no_auth()
    event['resource'] = "/reservation/{id}"
    event['path'] = "/reservation/12345678-resv-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-resv-0001-1234-abcdefghijkl"}

    return event


@pytest.fixture
def api_reserve_event():
    event = api_event_no_auth()
    event['resource'] = "/lists/{id}/reserve/{productid}/email/{email}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl/email/test.user3@gmail.com"
    event['httpMethod'] = "POST"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl", "email": "test.user3@gmail.com"}
    event['body'] = json.dumps({
        "quantity": 1,
        "title": "Child User1 1st Birthday",
        "product": {
            "type": "products",
            "brand": "Mamas and Papas",
            "details": "Balloon Print Zip All-in-One",
            "productUrl": "https://www.mamasandpapas.com/en-gb/balloon-print-zip-all-in-one/p/s94frd5",
            "imageUrl": "https://media.mamasandpapas.com/i/mamasandpapas/S94FRD5_HERO_AOP%20ZIP%20AIO/Clothing/Baby+Boys+Clothes/Welcome+to+the+World?$pdpimagemobile$"
        }
    })

    return event


@pytest.fixture
def api_unreserve_event():
    event = api_event_no_auth()
    event['resource'] = "/lists/reserve/{id}/email/{email}"
    event['path'] = "/lists/reserve/12345678-resv-0001-1234-abcdefghijkl/email/test.user2@gmail.com"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"id": "12345678-resv-0001-1234-abcdefghijkl", "email": "test.user2@gmail.com"}

    return event


@pytest.fixture
def api_delete_reservation_event():
    event = api_event_no_auth()
    event['resource'] = "/reservation/{id}"
    event['path'] = "/reservation/12345678-resv-0001-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"id": "12345678-resv-0001-1234-abcdefghijkl"}

    return event


@pytest.fixture
def api_update_product_event():
    event = api_event()
    event['resource'] = "/lists/{id}/product/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl",
    event['httpMethod'] = "PUT"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"quantity\": 4\n}"

    return event


@pytest.fixture
def api_update_product_with_notes_event():
    event = api_event()
    event['resource'] = "/lists/{id}/product/{productid}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl/product/12345678-prod-0001-1234-abcdefghijkl",
    event['httpMethod'] = "PUT"
    event['pathParameters'] = {"productid": "12345678-prod-0001-1234-abcdefghijkl", "id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = json.dumps({
        "quantity": 4,
        "notes": "Some custom user notes added"
    })

    return event


@pytest.fixture
def api_update_reservation_event():
    event = api_event_no_auth()
    event['resource'] = "/lists/reserve/{id}/email/{email}"
    event['path'] = "/lists/reserve/12345678-resv-0001-1234-abcdefghijkl/email/test.user2@gmail.com"
    event['httpMethod'] = "PUT"
    event['pathParameters'] = {"id": "12345678-resv-0001-1234-abcdefghijkl", "email": "test.user2@gmail.com"}
    event['body'] = json.dumps({
        "quantity": 2
    })

    return event


@pytest.fixture
def api_update_event():
    event = api_event()
    event['resource'] = "/lists/{id}"
    event['path'] = "/lists/12345678-list-0001-1234-abcdefghijkl"
    event['httpMethod'] = "PUT"
    event['pathParameters'] = {"id": "12345678-list-0001-1234-abcdefghijkl"}
    event['body'] = "{\n    \"title\": \"My Updated Title\",\n    \"description\": \"Updated description for the list.\",\n    \"eventDate\": \"25 December 2020\",\n    \"occasion\": \"Christmas\",\n    \"imageUrl\": \"/images/christmas-default.jpg\"\n}"

    return event


@pytest.fixture
def signup_with_u_and_p_event():
    return {
        "version": "1",
        "region": "eu-west-1",
        "userPoolId": "eu-west-1_vqox9Z8q7",
        "userName": "12345678-user-0003-1234-abcdefghijkl",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-unknown-unknown",
            "clientId": "61pt55apuqgj2jgbsfjmj1efn8"
        },
        "triggerSource": "PreSignUp_SignUp",
        "request": {
            "userAttributes": {
                "name": "Test User",
                "email": "test.user@gmail.com"
            },
            "validationData": None
        },
        "response": {
            "autoConfirmUser": "false",
            "autoVerifyEmail": "false",
            "autoVerifyPhone": "false"
        }
    }


@pytest.fixture
def signup_social_event():
    return {
        "version": "1",
        "region": "eu-west-1",
        "userPoolId": "eu-west-1_vqox9Z8q7",
        "userName": "randomid1234567890",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-unknown-unknown",
            "clientId": "61pt55apuqgj2jgbsfjmj1efn8"
        },
        "triggerSource": "PreSignUp_ExternalProvider",
        "request": {
            "userAttributes": {
                "cognito:email_alias": "",
                "name": "Test User",
                "cognito:phone_number_alias": "",
                "email": "test.user@gmail.com"
            },
            "validationData": None
        },
        "response": {
            "autoConfirmUser": "false",
            "autoVerifyEmail": "false",
            "autoVerifyPhone": "false"
        }
    }


@pytest.fixture
def postauth_not_verified_event():
    return {
        "version": "1",
        "region": "eu-west-1",
        "userPoolId": "eu-west-1_LW335q123",
        "userName": "72c2e9f9-0b20-454f-a117-fe5f1714d552",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-unknown-unknown",
            "clientId": "57l6m89od9d2s2vsjflig7dtkb"
        },
        "triggerSource": "PostAuthentication_Authentication",
        "request": {
            "userAttributes": {
                "sub": "72c2e9f9-0b20-454f-a117-fe5f1714d552",
                "cognito:user_status": "CONFIRMED",
                "identities": "[{\"userId\":\"117912944878954244147\",\"providerName\":\"Google\",\"providerType\":\"Google\",\"issuer\":null,\"primary\":false,\"dateCreated\":1605522871216}]",
                "email_verified": "false",
                "name": "Test User",
                "email": "test.exists@gmail.com"
            },
            "newDeviceUsed": "false"
        },
        "response": {}
    }


@pytest.fixture
def postauth_verified_event():
    return {
        "version": "1",
        "region": "eu-west-1",
        "userPoolId": "eu-west-1_LW335q123",
        "userName": "72c2e9f9-0b20-454f-a117-fe5f1714d552",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-unknown-unknown",
            "clientId": "57l6m89od9d2s2vsjflig7dtkb"
        },
        "triggerSource": "PostAuthentication_Authentication",
        "request": {
            "userAttributes": {
                "sub": "72c2e9f9-0b20-454f-a117-fe5f1714d552",
                "cognito:user_status": "CONFIRMED",
                "identities": "[{\"userId\":\"117912944878954244147\",\"providerName\":\"Google\",\"providerType\":\"Google\",\"issuer\":null,\"primary\":false,\"dateCreated\":1605522871216}]",
                "email_verified": "true",
                "name": "Test User",
                "email": "test.exists@gmail.com"
            },
            "newDeviceUsed": "false"
        },
        "response": {}
    }
