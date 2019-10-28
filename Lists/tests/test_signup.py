import pytest
import uuid
import os
import re
import json
import copy
import boto3
from moto import mock_dynamodb2, mock_cognitoidp
from lists import signup

import sys
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


@pytest.fixture
def signup_with_u_and_p_event():
    """ Generates API GW Event"""

    return {
        "version": "1",
        "region": "eu-west-1",
        "userPoolId": "eu-west-1_vqox9Z8q7",
        "userName": "5ba4554b-4423-4ea1-b13a-6777b065fc5c",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-unknown-unknown",
            "clientId": "61pt55apuqgj2jgbsfjmj1efn8"
        },
        "triggerSource": "PreSignUp_SignUp",
        "request": {
            "userAttributes": {
                "email": "test.user@gmail.com"
            },
            "validationData": "null"
        },
        "response": {
            "autoConfirmUser": "false",
            "autoVerifyEmail": "false",
            "autoVerifyPhone": "false"
        }
    }


@pytest.fixture
def signup_with_google_event():
    """ Generates API GW Event"""

    return {
        "version": "1",
        "region": "eu-west-1",
        "userPoolId": "eu-west-1_vqox9Z8q7",
        "userName": "Google_109769169322789401234",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-unknown-unknown",
            "clientId": "61pt55apuqgj2jgbsfjmj1efn8"
        },
        "triggerSource": "PreSignUp_ExternalProvider",
        "request": {
            "userAttributes": {
                "cognito:email_alias": "",
                "cognito:phone_number_alias": "",
                "email": "test.user@gmail.com"
            },
            "validationData": {}
        },
        "response": {
            "autoConfirmUser": "false",
            "autoVerifyEmail": "false",
            "autoVerifyPhone": "false"
        }
    }


@pytest.fixture
def signup_with_facebook_event():
    """ Generates API GW Event"""

    return {
        "version": "1",
        "region": "eu-west-1",
        "userPoolId": "eu-west-1_vqox9Z8q7",
        "userName": "Facebook_10156460942006789",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-unknown-unknown",
            "clientId": "61pt55apuqgj2jgbsfjmj1efn8"
        },
        "triggerSource": "PreSignUp_ExternalProvider",
        "request": {
            "userAttributes": {
                "cognito:email_alias": "",
                "cognito:phone_number_alias": "",
                "email": "test.user@gmail.com"
            },
            "validationData": {}
        },
        "response": {
            "autoConfirmUser": "false",
            "autoVerifyEmail": "false",
            "autoVerifyPhone": "false"
        }
    }


@pytest.fixture
def signup_with_amazon_event():
    """ Generates API GW Event"""

    return {
        "version": "1",
        "region": "eu-west-1",
        "userPoolId": "eu-west-1_vqox9Z8q7",
        "userName": "LoginWithAmazon_amzn1.account.AH2EWIJQPC4QJNTUDTVRABCDEFGH",
        "callerContext": {
            "awsSdkVersion": "aws-sdk-unknown-unknown",
            "clientId": "61pt55apuqgj2jgbsfjmj1efn8"
        },
        "triggerSource": "PreSignUp_ExternalProvider",
        "request": {
            "userAttributes": {
                "cognito:email_alias": "",
                "cognito:phone_number_alias": "",
                "email": "test.user@gmail.com"
            },
            "validationData": {}
        },
        "response": {
            "autoConfirmUser": "false",
            "autoVerifyEmail": "false",
            "autoVerifyPhone": "false"
        }
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

    items = [
        {"PK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "SK": "USER#eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c", "email": "test.join@gmail.com", "name": "Test User", "userId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c"},
    ]

    for item in items:
        table.put_item(TableName=table_name, Item=item)

    yield
    # teardown: stop moto server
    mock.stop()


@pytest.fixture
def cognito_mock():
    pool_name = 'ewelists-unittest'

    mock = mock_cognitoidp()
    mock.start()

    client = boto3.client('cognito-idp', region_name='eu-west-1')

    user_pool_id = client.create_user_pool(
        PoolName=pool_name,
    )["UserPool"]["Id"]

    username = str(uuid.uuid4())

    client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[
            {"Name": "email", "Value": 'test.user@gmail.com'}
        ],
    )

    yield
    # teardown: stop moto server
    mock.stop()


class TestGetUserFromEvent:
    def test_cognito_user(self, signup_with_u_and_p_event):
        user = signup.get_user_from_event(signup_with_u_and_p_event)
        assert user['type'] == "Cognito", "Attribute type was not Cognito."
        assert user['username'] == "5ba4554b-4423-4ea1-b13a-6777b065fc5c", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."

    def test_google_user(self, signup_with_google_event):
        user = signup.get_user_from_event(signup_with_google_event)
        assert user['type'] == "Google", "Attribute type was not Google."
        assert user['username'] == "109769169322789401234", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."

    def test_facebook_user(self, signup_with_facebook_event):
        user = signup.get_user_from_event(signup_with_facebook_event)
        assert user['type'] == "Facebook", "Attribute type was not Facebook."
        assert user['username'] == "10156460942006789", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."

    def test_amazon_user(self, signup_with_amazon_event):
        user = signup.get_user_from_event(signup_with_amazon_event)
        assert user['type'] == "LoginWithAmazon", "Attribute type was not LoginWithAmazon."
        assert user['username'] == "AH2EWIJQPC4QJNTUDTVRABCDEFGH", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."


class TestGetUserFromUserpool:
    def test_user_exists(self, cognito_mock):
        client = boto3.client('cognito-idp', region_name='eu-west-1')
        list_response = client.list_user_pools(MaxResults=123)
        user_pool_id = list_response['UserPools'][0]['Id']

        result = signup.get_user_from_userpool(user_pool_id, 'test.user@gmail.com')
        assert result['exists'], "User did not exist in userpool"
        assert len(result['user_sub']) == 36

        expected_attributes = [
            {'Name': 'email', 'Value': 'test.user@gmail.com'}
        ]
        assert result['user_attributes'] == expected_attributes

    @pytest.mark.skip(reason="Filter is not implemented with moto: https://github.com/spulec/moto/issues/1944")
    def test_user_does_not_exist_in_userpool(self, cognito_mock):
        client = boto3.client('cognito-idp', region_name='eu-west-1')
        list_response = client.list_user_pools(MaxResults=123)
        user_pool_id = list_response['UserPools'][0]['Id']

        result = signup.get_user_from_userpool(user_pool_id, 'blah@gmail.com')
        assert not result['exists'], "User existed in userpool"


class TestCreateUserInListsDB:
    def test_create_new_user(self, dynamodb_mock):
        email = 'test.user@gmail.com'
        sub = '71b579e5-ea02-4bed-a782-f12889658e73'
        created = signup.create_user_in_lists_db('lists-unittest', sub, email)

        assert created, "User was not created in table."

    def test_create_user_with_bad_table_name(self, dynamodb_mock):
        email = 'test.user@gmail.com'
        sub = '71b579e5-ea02-4bed-a782-f12889658e73'
        with pytest.raises(Exception) as e:
            signup.create_user_in_lists_db('lists-unittes', sub, email)
        assert str(e.value) == "User entry could not be created.", "Exception not as expected."


class TestLinkAccounts:
    @pytest.mark.skip(reason="The admin_link_provider_for_user action has not been implemented")
    def test_link_google_account(self, cognito_mock):
        client = boto3.client('cognito-idp', region_name='eu-west-1')
        list_response = client.list_user_pools(MaxResults=123)
        user_pool_id = list_response['UserPools'][0]['Id']

        email = 'test.join@gmail.com'
        existing_sub = 'db9476fd-de77-4977-839f-4f943ff5d68c'
        new_type = 'Google'
        new_id = '109769169322789401234'

        link_result = signup.link_accounts(user_pool_id, email, existing_sub, new_type, new_id)


class TestCreateNewCognitoUser:
    def test_create_new_cognito_user(self, cognito_mock):
        client = boto3.client('cognito-idp', region_name='eu-west-1')
        list_response = client.list_user_pools(MaxResults=123)
        user_pool_id = list_response['UserPools'][0]['Id']

        email = 'test.user@gmail.com'

        result = signup.create_new_cognito_user(user_pool_id, email)

        assert result['created'], "New account was not created."
        assert len(result['user_id']) == 36, "New user id was not expected lenghth."

# As link account tests not implemented, not able to test whole logic.
# class TestHandler:
