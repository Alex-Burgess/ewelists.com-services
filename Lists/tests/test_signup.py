import pytest
import uuid
import os
import mock
import boto3
from moto import mock_cognitoidp
from lists import signup, logger

log = logger.setup_test_logger()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'TEMPLATE_NAME', 'Welcome-Unittest')
    monkeypatch.setitem(os.environ, 'DOMAIN_NAME', 'https://unittest.ewelists.com')

    client = boto3.client('cognito-idp', region_name='eu-west-1')
    list_response = client.list_user_pools(MaxResults=1)
    monkeypatch.setitem(os.environ, 'USERPOOL_ID', list_response['UserPools'][0]['Id'])

    return monkeypatch


class TestGetUserFromEvent:
    def test_cognito_user(self, signup_with_u_and_p_event):
        user = signup.get_user_from_event(signup_with_u_and_p_event)
        assert user['type'] == "Cognito", "Attribute type was not Cognito."
        assert user['username'] == "12345678-user-0003-1234-abcdefghijkl", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "Test User", "Attribute name was not as expected."

    def test_google_user(self, signup_social_event):
        signup_social_event['userName'] = "Google_109769169322789401234"
        user = signup.get_user_from_event(signup_social_event)
        assert user['type'] == "Google", "Attribute type was not Google."
        assert user['username'] == "109769169322789401234", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "Test User", "Attribute name was not as expected."

    def test_facebook_user(self, signup_social_event):
        signup_social_event['userName'] = "Facebook_10156460942006789"
        user = signup.get_user_from_event(signup_social_event)
        assert user['type'] == "Facebook", "Attribute type was not Facebook."
        assert user['username'] == "10156460942006789", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "Test User", "Attribute name was not as expected."

    def test_amazon_user(self, signup_social_event):
        signup_social_event['userName'] = "LoginWithAmazon_amzn1.account.AH2EWIJQPC4QJNTUDTVRABCDEFGH"
        user = signup.get_user_from_event(signup_social_event)
        assert user['type'] == "LoginWithAmazon", "Attribute type was not LoginWithAmazon."
        assert user['username'] == "amzn1.account.AH2EWIJQPC4QJNTUDTVRABCDEFGH", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "Test User", "Attribute name was not as expected."

    def test_with_no_name(self, signup_with_u_and_p_event):
        del signup_with_u_and_p_event['request']['userAttributes']['name']
        user = signup.get_user_from_event(signup_with_u_and_p_event)
        assert user['type'] == "Cognito", "Attribute type was not Cognito."
        assert user['username'] == "12345678-user-0003-1234-abcdefghijkl", "Attribute username was not as expected."
        assert user['email'] == "test.user@gmail.com", "Attribute email was not as expected."
        assert user['name'] == "", "Attribute name was not as expected."

    def test_googlemail_dot_com_user(self, signup_social_event):
        signup_social_event['userName'] = "Google_109769169322789401234"
        signup_social_event['request']['userAttributes']['email'] = "test.user@googlemail.com"
        user = signup.get_user_from_event(signup_social_event)
        assert user['type'] == "Google", "Attribute type was not Google."
        assert user['username'] == "109769169322789401234", "Attribute username was not as expected."
        assert user['email'] == "test.user@googlemail.com", "Attribute email was not as expected."
        assert user['name'] == "Test User", "Attribute name was not as expected."


class TestCheckNoAlternateGoogleEmail:
    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[]))
    def test_no_user_exist(self, cognito_mock, user_pool_id):
        assert signup.check_no_alternate_google_email(user_pool_id, 'test.user1000@gmail.com'), "User should not exist."

    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[]))
    def test_actual_email_exists(self, cognito_mock, user_pool_id):
        assert signup.check_no_alternate_google_email(user_pool_id, 'test.user@gmail.com'), "No alternate should not exist."

    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[
        {'Username': 'e8853ecf-b11e-44b9-81c7-059ec15dfcda', 'Attributes': [{'Name': 'email', 'Value': 'test.exists@googlemail.com'}], 'UserCreateDate': 'Apr 27, 2020 12:45:05 PM', 'UserLastModifiedDate': 'Apr 27, 2020 12:45:05 PM', 'Enabled': True, 'UserStatus': 'FORCE_CHANGE_PASSWORD', 'MFAOptions': []}
    ]))
    def test_gmail_alternate_exists(self, cognito_mock, user_pool_id):
        with pytest.raises(Exception) as e:
            signup.check_no_alternate_google_email(user_pool_id, 'test.exists@googlemail.com')
        assert str(e.value) == "User exists with different google email address test.exists@gmail.com.", "A gmail alternate should not exist."

    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[
        {'Username': 'e8853ecf-b11e-44b9-81c7-059ec15dfcda', 'Attributes': [{'Name': 'email', 'Value': 'test.new@googlemail.com'}], 'UserCreateDate': 'Apr 27, 2020 12:45:05 PM', 'UserLastModifiedDate': 'Apr 27, 2020 12:45:05 PM', 'Enabled': True, 'UserStatus': 'FORCE_CHANGE_PASSWORD', 'MFAOptions': []}
    ]))
    def test_googlemail_alternate_exists(self, cognito_mock, user_pool_id):
        # Create googlemail user
        client = boto3.client('cognito-idp', region_name='eu-west-1')
        client.admin_create_user(
            UserPoolId=user_pool_id,
            Username=str(uuid.uuid4()),
            UserAttributes=[{"Name": "email", "Value": 'test.new@googlemail.com'}]
        )

        with pytest.raises(Exception) as e:
            signup.check_no_alternate_google_email(user_pool_id, 'test.new@googlemail.com')
        assert str(e.value) == "User exists with different google email address test.new@gmail.com.", "A googlemail alternate should not exist."


class TestSwitchGoogleDomain:
    def test_switch_from_gmail(self):
        alternate_email = signup.switch_google_domain('test.user@gmail.com')
        assert alternate_email == 'test.user@googlemail.com', 'Email should be @googlemail.com'

    def test_switch_from_googlemail(self):
        alternate_email = signup.switch_google_domain('test.user@googlemail.com')
        assert alternate_email == 'test.user@gmail.com', 'Email should be @gmail.com'


class TestGetUserFromUserpool:
    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[
        {'Username': '25cc41dc-2495-450f-b2a1-d4103296534c', 'Attributes': [{'Name': 'email', 'Value': 'test.exists@gmail.com'}]}
    ]))
    def test_user_exists(self, cognito_mock, user_pool_id):
        result = signup.get_user_from_userpool(user_pool_id, 'test.exists@gmail.com')
        assert result['exists'], "User did not exist in userpool"
        assert len(result['user_sub']) == 36

        expected_attributes = [
            {'Name': 'email', 'Value': 'test.exists@gmail.com'}
        ]
        assert result['user_attributes'] == expected_attributes

    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[]))
    def test_user_does_not_exist_in_userpool(self, cognito_mock, user_pool_id):
        result = signup.get_user_from_userpool(user_pool_id, 'blah@gmail.com')
        assert not result['exists'], "User existed in userpool"


class TestCreateUserInListsDB:
    def test_create_new_user(self, dynamodb_mock):
        email = 'test.user10@gmail.com'
        name = 'Test User10'
        sub = '12345678-user-0010-1234-abcdefghijkl'
        assert signup.create_user_in_lists_db('lists-unittest', sub, email, name), "User was not created in table."

        # Check the table was updated with right number of items
        dynamodb = boto3.client('dynamodb', region_name='eu-west-1')

        response = dynamodb.get_item(
            TableName='lists-unittest',
            Key={
                'PK': {'S': "USER#12345678-user-0010-1234-abcdefghijkl"},
                'SK': {'S': "USER#12345678-user-0010-1234-abcdefghijkl"}
            }
        )

        expected_item = {
            "PK": {"S": "USER#12345678-user-0010-1234-abcdefghijkl"},
            "SK": {"S": "USER#12345678-user-0010-1234-abcdefghijkl"},
            "email": {"S": "test.user10@gmail.com"},
            "name": {"S": "Test User10"},
            "userId": {"S": "12345678-user-0010-1234-abcdefghijkl"}
        }

        assert response['Item'] == expected_item

    def test_create_user_with_bad_table_name(self, dynamodb_mock):
        email = 'test.user@gmail.com'
        name = 'Test User'
        sub = '12345678-user-fail-1234-abcdefghijkl'
        with pytest.raises(Exception) as e:
            signup.create_user_in_lists_db('lists-unittes', sub, email, name)
        assert str(e.value) == "User entry could not be created for test.user@gmail.com.", "Exception not as expected."

    def test_create_user_with_no_name(self, dynamodb_mock):
        email = 'test.user10@gmail.com'
        name = ''
        sub = '12345678-user-0010-1234-abcdefghijkl'
        assert signup.create_user_in_lists_db('lists-unittest', sub, email, name), "User was not created in table."


class TestCognitoActions:
    @pytest.mark.skip(reason="The admin_link_provider_for_user action has not been implemented")
    def test_link_google_account(self, cognito_mock, user_pool_id):
        email = 'test.join@gmail.com'
        existing_sub = '12345678-user-0001-1234-abcdefghijkl'
        new_type = 'Google'
        new_id = '109769169322789401234'

        link_result = signup.link_accounts(user_pool_id, email, existing_sub, new_type, new_id)
        assert link_result

    @pytest.mark.skip(reason="Filter is not implemented with moto: https://github.com/spulec/moto/issues/1944")
    def test_get_user_client_call(self, cognito_mock, user_pool_id):
        users = signup.get_user_client_call(user_pool_id, 'test.exists@gmail.com')
        assert len(users) == 1


class TestCreateNewCognitoUser:
    def test_create_new_cognito_user(self, cognito_mock, user_pool_id):
        result = signup.create_new_cognito_user(user_pool_id, 'test.user@gmail.com', 'Test User')

        assert result['created'], "New account was not created."
        assert len(result['user_id']) == 19, "New user id was not expected lenghth."


class TestCreateEmailData:
    def test_create_email_data(self):
        domain_name = 'http://localhost:3000'
        name = 'Test User'

        data = signup.create_email_data(domain_name, name)

        expected_data = {
            "name": "Test User"
        }

        assert data == expected_data, "Email data json object was not as expected."


@mock_cognitoidp
@mock.patch("lists.common.send_email", mock.MagicMock(return_value=[True]))
@mock.patch("lists.signup.link_accounts", mock.MagicMock(return_value=[True]))
@mock.patch("lists.signup.set_random_password", mock.MagicMock(return_value=[True]))
class TestHandler:
    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[]))
    def test_sign_up(self, cognito_mock, signup_with_u_and_p_event, env_vars, dynamodb_mock):
        response = signup.handler(signup_with_u_and_p_event, None)
        assert response == signup_with_u_and_p_event, "Event was not as expected."

    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[]))
    def test_sign_up_with_google(self, cognito_mock, signup_social_event, env_vars, dynamodb_mock):
        signup_social_event['userName'] = "Google_109769169322789401234"
        with pytest.raises(Exception) as e:
            signup.handler(signup_social_event, None)
        assert str(e.value) == "Google Signup", "Exception not as expected."

    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[]))
    def test_sign_up_with_fb(self, cognito_mock, signup_social_event, env_vars, dynamodb_mock):
        signup_social_event['userName'] = "Facebook_10156460942006789"
        with pytest.raises(Exception) as e:
            signup.handler(signup_social_event, None)
        assert str(e.value) == "Facebook Signup", "Exception not as expected."

    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[]))
    def test_sign_up_with_amazon(self, cognito_mock, signup_social_event, env_vars, dynamodb_mock):
        signup_social_event['userName'] = "LoginWithAmazon_amzn1.account.AH2EWIJQPC4QJNTUDTVRABCDEFGH"
        with pytest.raises(Exception) as e:
            signup.handler(signup_social_event, None)
        assert str(e.value) == "LoginWithAmazon Signup", "Exception not as expected."

    @mock.patch("lists.signup.check_no_alternate_google_email", mock.MagicMock(return_value=False))
    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[
        {'Username': '25cc41dc-2495-450f-b2a1-d4103296534c', 'Attributes': [{'Name': 'email', 'Value': 'test.exists@gmail.com'}]}
    ]))
    def test_link_accounts_with_social_first(self, signup_social_event, signup_with_u_and_p_event, monkeypatch, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        monkeypatch.setitem(os.environ, 'TEMPLATE_NAME', 'Welcome-Unittest')
        monkeypatch.setitem(os.environ, 'DOMAIN_NAME', 'https://unittest.ewelists.com')

        client = boto3.client('cognito-idp', region_name='eu-west-1')
        user_pool_id = client.create_user_pool(PoolName='ewelists-unittest')["UserPool"]["Id"]
        monkeypatch.setitem(os.environ, 'USERPOOL_ID', user_pool_id)

        # TODO - Initial sign up is failing because we have to mock client.list_users as it is not full implemented in moto.
        #
        # Sign up with amazon
        # signup_social_event['userName'] = "LoginWithAmazon_amzn1.account.AH2EWIJQPC4QJNTUDTVRABCDEFGH"
        # with pytest.raises(Exception) as e:
        #     signup.handler(signup_social_event, None)
        # assert str(e.value) == "LoginWithAmazon Signup", "Exception not as expected."

        # Sign up with google - should link
        signup_social_event['userName'] = "Google_109769169322789401234"
        with pytest.raises(Exception) as e:
            signup.handler(signup_social_event, None)
        assert str(e.value) == "Google LinkedLogon", "Exception not as expected."

        # Sign up with facebook - should link
        signup_social_event['userName'] = "Facebook_10156460942006789"
        with pytest.raises(Exception) as e:
            signup.handler(signup_social_event, None)
        assert str(e.value) == "Facebook LinkedLogon", "Exception not as expected."

        with pytest.raises(Exception) as e:
            signup.handler(signup_with_u_and_p_event, None)
        assert str(e.value) == "Cognito LinkedLogon", "Exception not as expected."

    @mock.patch("lists.signup.check_no_alternate_google_email", mock.MagicMock(return_value=False))
    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[
        {'Username': '25cc41dc-2495-450f-b2a1-d4103296534c', 'Attributes': [{'Name': 'email', 'Value': 'test.exists@gmail.com'}]}
    ]))
    def test_link_accounts_with_u_and_p_first(self, cognito_mock, signup_social_event, env_vars, dynamodb_mock):
        # Sign up with google - should link
        signup_social_event['userName'] = "Google_109769169322789401234"
        signup_social_event['request']['userAttributes']['email'] = "test.exists@gmail.com"

        with pytest.raises(Exception) as e:
            signup.handler(signup_social_event, None)
        assert str(e.value) == "Google LinkedLogon", "Exception not as expected."

    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[
        {'Username': 'e8853ecf-b11e-44b9-81c7-059ec15dfcda', 'Attributes': [{'Name': 'email', 'Value': 'test.exists@gmail.com'}], 'UserCreateDate': 'Apr 27, 2020 12:45:05 PM', 'UserLastModifiedDate': 'Apr 27, 2020 12:45:05 PM', 'Enabled': True, 'UserStatus': 'FORCE_CHANGE_PASSWORD', 'MFAOptions': []}
    ]))
    def test_alternate_gmail_exists(self, cognito_mock, signup_with_u_and_p_event, env_vars, dynamodb_mock):
        signup_with_u_and_p_event["request"]["userAttributes"]["email"] = "test.exists@googlemail.com"

        with pytest.raises(Exception) as e:
            signup.handler(signup_with_u_and_p_event, None)
        assert str(e.value) == "User exists with different google email address test.exists@gmail.com.", "A googlemail alternate should not exist."

    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[
        {'Username': 'e8853ecf-b11e-44b9-81c7-059ec15dfcda', 'Attributes': [{'Name': 'email', 'Value': 'test.exists2@googlemail.com'}], 'UserCreateDate': 'Apr 27, 2020 12:45:05 PM', 'UserLastModifiedDate': 'Apr 27, 2020 12:45:05 PM', 'Enabled': True, 'UserStatus': 'FORCE_CHANGE_PASSWORD', 'MFAOptions': []}
    ]))
    def test_alternate_google_mail_exists(self, cognito_mock, signup_with_u_and_p_event, env_vars, dynamodb_mock):
        signup_with_u_and_p_event["request"]["userAttributes"]["email"] = "test.exists2@gmail.com"

        with pytest.raises(Exception) as e:
            signup.handler(signup_with_u_and_p_event, None)
        assert str(e.value) == "User exists with different google email address test.exists2@googlemail.com.", "A googlemail alternate should not exist."

    @mock.patch("lists.signup.get_user_client_call", mock.MagicMock(return_value=[
        {'Username': 'e8853ecf-b11e-44b9-81c7-059ec15dfcda', 'Attributes': [{'Name': 'email', 'Value': 'test.exists@gmail.com'}], 'UserCreateDate': 'Apr 27, 2020 12:45:05 PM', 'UserLastModifiedDate': 'Apr 27, 2020 12:45:05 PM', 'Enabled': True, 'UserStatus': 'FORCE_CHANGE_PASSWORD', 'MFAOptions': []}
    ]))
    def test_alternate_google_mail_from_social_exists(self, cognito_mock, signup_social_event, env_vars, dynamodb_mock):
        signup_social_event['userName'] = "Google_109769169322789401234"
        signup_social_event['request']['userAttributes']['email'] = "test.exists@googlemail.com"

        with pytest.raises(Exception) as e:
            signup.handler(signup_social_event, None)
        assert str(e.value) == "User exists with different google email address test.exists@gmail.com.", "A googlemail alternate should not exist."
