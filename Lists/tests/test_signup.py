import pytest
import uuid
import boto3
from moto import mock_dynamodb2, mock_cognitoidp
from lists import signup, logger
from tests import fixtures

log = logger.setup_logger()


@pytest.fixture
def signup_with_u_and_p_event():
    event = fixtures.signup_event()
    return event


@pytest.fixture
def signup_with_google_event():
    event = fixtures.signup_social_event()
    event['userName'] = "Google_109769169322789401234"
    return event


@pytest.fixture
def signup_with_facebook_event():
    event = fixtures.signup_social_event()
    event['userName'] = "Facebook_10156460942006789"
    return event


@pytest.fixture
def signup_with_amazon_event():
    event = fixtures.signup_social_event()
    event['userName'] = "LoginWithAmazon_amzn1.account.AH2EWIJQPC4QJNTUDTVRABCDEFGH"
    return event


@pytest.fixture
def signup_event_with_no_name():
    event = fixtures.signup_event()
    del event['request']['userAttributes']['name']

    return event


@pytest.fixture
def dynamodb_mock():
    mock = mock_dynamodb2()
    mock.start()
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

    table = dynamodb.create_table(
        TableName='lists-unittest',
        KeySchema=[{'AttributeName': 'PK', 'KeyType': 'HASH'}, {'AttributeName': 'SK', 'KeyType': 'RANGE'}],
        AttributeDefinitions=[{'AttributeName': 'PK', 'AttributeType': 'S'}, {'AttributeName': 'SK', 'AttributeType': 'S'}],
        ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
        GlobalSecondaryIndexes=[{
            'IndexName': 'SK-index',
            'KeySchema': [{'AttributeName': 'SK', 'KeyType': 'HASH'}, {'AttributeName': 'PK', 'KeyType': 'RANGE'}],
            'Projection': {
                'ProjectionType': 'ALL'
            }
        }]
    )

    items = [
        {"PK": "USER#12345678-user-0001-1234-abcdefghijkl", "SK": "USER#12345678-user-0001-1234-abcdefghijkl", "email": "test.join@gmail.com", "name": "Test User", "userId": "12345678-user-0001-1234-abcdefghijkl"},
        {"PK": "LIST#12345678-list-0001-1234-abcdefghijkl", "SK": "PENDING#test.user4@gmail.com", "shared_user_email": "test.user4@gmail.com", "title": "Child User1 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0001-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": 1573739584, "description": "A gift list for Child User1 birthday.", "eventDate": "31 October 2018", "imageUrl": "/images/celebration-default.jpg"},
        {"PK": "LIST#12345678-list-0002-1234-abcdefghijkl", "SK": "PENDING#test.user4@gmail.com", "shared_user_email": "test.user4@gmail.com", "title": "Child User2 1st Birthday", "occasion": "Birthday", "listId": "12345678-list-0002-1234-abcdefghijkl", "listOwner": "12345678-user-0001-1234-abcdefghijkl", "createdAt": 1573739590, "description": "A gift list for Child User2 birthday.", "eventDate": "31 October 2018", "imageUrl": "/images/celebration-default.jpg"}
    ]

    for item in items:
        table.put_item(TableName='lists-unittest', Item=item)

    yield
    mock.stop()


@pytest.fixture
def cognito_mock():
    mock = mock_cognitoidp()
    mock.start()
    client = boto3.client('cognito-idp', region_name='eu-west-1')

    user_pool_id = client.create_user_pool(PoolName='ewelists-unittest')["UserPool"]["Id"]
    username = str(uuid.uuid4())

    client.admin_create_user(
        UserPoolId=user_pool_id,
        Username=username,
        UserAttributes=[{"Name": "email", "Value": 'test.user@gmail.com'}]
    )

    yield
    mock.stop()


class TestGetUserFromEvent:
    def test_cognito_user(self, signup_with_u_and_p_event):
        user = signup.get_user_from_event(signup_with_u_and_p_event)
        assert user['type'] == "Cognito", "Attribute type was not Cognito."
        assert user['username'] == "12345678-user-0003-1234-abcdefghijkl", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "Test User", "Attribute name was not as expected."

    def test_google_user(self, signup_with_google_event):
        user = signup.get_user_from_event(signup_with_google_event)
        assert user['type'] == "Google", "Attribute type was not Google."
        assert user['username'] == "109769169322789401234", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "Test User", "Attribute name was not as expected."

    def test_googlemail_dot_com_user(self, signup_with_google_event):
        signup_with_google_event['request']['userAttributes']['email'] = "test.user@googlemail.com"
        user = signup.get_user_from_event(signup_with_google_event)
        assert user['type'] == "Google", "Attribute type was not Google."
        assert user['username'] == "109769169322789401234", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "Test User", "Attribute name was not as expected."

    def test_facebook_user(self, signup_with_facebook_event):
        user = signup.get_user_from_event(signup_with_facebook_event)
        assert user['type'] == "Facebook", "Attribute type was not Facebook."
        assert user['username'] == "10156460942006789", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "Test User", "Attribute name was not as expected."

    def test_amazon_user(self, signup_with_amazon_event):
        user = signup.get_user_from_event(signup_with_amazon_event)
        assert user['type'] == "LoginWithAmazon", "Attribute type was not LoginWithAmazon."
        assert user['username'] == "amzn1.account.AH2EWIJQPC4QJNTUDTVRABCDEFGH", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "Test User", "Attribute name was not as expected."

    def test_with_no_name(self, signup_event_with_no_name):
        user = signup.get_user_from_event(signup_event_with_no_name)
        assert user['type'] == "Cognito", "Attribute type was not Cognito."
        assert user['username'] == "12345678-user-0003-1234-abcdefghijkl", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "", "Attribute name was not as expected."


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
        email = 'test.user2@gmail.com'
        name = 'Test User2'
        sub = '12345678-user-0002-1234-abcdefghijkl'
        assert signup.create_user_in_lists_db('lists-unittest', sub, email, name), "User was not created in table."

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={
                'PK': {'S': "USER#12345678-user-0002-1234-abcdefghijkl"},
                'SK': {'S': "USER#12345678-user-0002-1234-abcdefghijkl"}
            }
        )

        expected_item = {
            "PK": {"S": "USER#12345678-user-0002-1234-abcdefghijkl"},
            "SK": {"S": "USER#12345678-user-0002-1234-abcdefghijkl"},
            "email": {"S": "test.user2@gmail.com"},
            "name": {"S": "Test User2"},
            "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}
        }

        assert response['Item'] == expected_item

    def test_create_user_with_bad_table_name(self, dynamodb_mock):
        email = 'test.user@gmail.com'
        name = 'Test User2'
        sub = '12345678-user-0002-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            signup.create_user_in_lists_db('lists-unittes', sub, email, name)
        assert str(e.value) == "User entry could not be created.", "Exception not as expected."

    def test_create_user_with_no_name(self, dynamodb_mock):
        email = 'test.user@gmail.com'
        name = ''
        sub = '12345678-user-0002-1234-abcdefghijkl'
        assert signup.create_user_in_lists_db('lists-unittest', sub, email, name), "User was not created in table."


class TestCreatedSharedItems:
    @pytest.mark.skip(reason="transact_write_items is not implemented for moto")
    def test_created_shared_item(self, dynamodb_mock):
        pending_items = [
            {
                "PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"},
                "SK": {'S': "PENDING#test.user4@gmail.com"},
                "shared_user_email": {'S': "test.user4@gmail.com"},
                "title": {'S': "Child User1 1st Birthday"},
                "occasion": {'S': "Birthday"},
                "listId": {'S': "12345678-list-0001-1234-abcdefghijkl"},
                "listOwner": {'S': "12345678-user-0001-1234-abcdefghijkl"},
                "createdAt": {'N': "1573739584"},
                "description": {'S': "A gift list for Child User1 birthday."},
                "eventDate": {'S': "31 October 2018"},
                "imageUrl": {'S': "/images/celebration-default.jpg"}
            },
            {
                "PK": {"S": "LIST#12345678-list-0002-1234-abcdefghijkl"},
                "SK": {'S': "PENDING#test.user4@gmail.com"},
                "shared_user_email": {'S': "test.user4@gmail.com"},
                "title": {'S': "Child User2 1st Birthday"},
                "occasion": {'S': "Birthday"},
                "listId": {'S': "12345678-list-0002-1234-abcdefghijkl"},
                "listOwner": {'S': "12345678-user-0001-1234-abcdefghijkl"},
                "createdAt": {'N': "1573739590"},
                "description": {'S': "A gift list for Child User2 birthday."},
                "eventDate": {'S': "31 October 2018"},
                "imageUrl": {'S': "/images/celebration-default.jpg"}
            }
        ]
        assert signup.create_shared_items('lists-unittest', pending_items, '12345678-user-0004-1234-abcdefghijkl', 'Test User4')


class TestLinkAccounts:
    @pytest.mark.skip(reason="The admin_link_provider_for_user action has not been implemented")
    def test_link_google_account(self, cognito_mock):
        client = boto3.client('cognito-idp', region_name='eu-west-1')
        list_response = client.list_user_pools(MaxResults=123)
        user_pool_id = list_response['UserPools'][0]['Id']

        email = 'test.join@gmail.com'
        existing_sub = '12345678-user-0001-1234-abcdefghijkl'
        new_type = 'Google'
        new_id = '109769169322789401234'

        link_result = signup.link_accounts(user_pool_id, email, existing_sub, new_type, new_id)
        assert link_result


class TestCreateNewCognitoUser:
    def test_create_new_cognito_user(self, cognito_mock):
        client = boto3.client('cognito-idp', region_name='eu-west-1')
        list_response = client.list_user_pools(MaxResults=123)
        user_pool_id = list_response['UserPools'][0]['Id']

        email = 'test.user@gmail.com'
        name = 'Test User'

        result = signup.create_new_cognito_user(user_pool_id, email, name)

        assert result['created'], "New account was not created."
        assert len(result['user_id']) == 19, "New user id was not expected lenghth."


# As link account tests not implemented, not able to test whole logic.
# class TestHandler:
