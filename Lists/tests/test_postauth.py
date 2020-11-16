import pytest
import os
# import mock
import boto3
from moto import mock_cognitoidp
from lists import postauth, logger

log = logger.setup_test_logger()


@pytest.fixture
def env_vars(monkeypatch):
    client = boto3.client('cognito-idp', region_name='eu-west-1')
    list_response = client.list_user_pools(MaxResults=1)
    monkeypatch.setitem(os.environ, 'USERPOOL_ID', list_response['UserPools'][0]['Id'])

    return monkeypatch


@mock_cognitoidp
class TestHandler:
    def test_email_verified(self, cognito_mock, postauth_verified_event, env_vars):
        response = postauth.handler(postauth_verified_event, None)
        assert response == postauth_verified_event, "Event was not as expected."

    def test_email_notverified(self, cognito_mock, postauth_not_verified_event, env_vars):
        response = postauth.handler(postauth_not_verified_event, None)
        assert response == postauth_not_verified_event, "Event was not as expected."

    def test_unexpected_exception(self, cognito_mock, postauth_not_verified_event, env_vars):
        postauth_not_verified_event['request']['userAttributes'] = None
        response = postauth.handler(postauth_not_verified_event, None)
        assert response == postauth_not_verified_event, "Event was not as expected."


class TestGetUser:
    def test_get_user_email(self, postauth_verified_event):
        assert postauth.get_email(postauth_verified_event) == 'test.exists@gmail.com'

    def test_no_user_email(self):
        with pytest.raises(Exception) as e:
            assert postauth.get_email({})
        assert str(e.value) == "Could not get users email as not in event.", "Exception was not as expected."


class TestCheckEmailVerified:
    def test_email_verified(self, postauth_verified_event):
        assert postauth.check_email_verified(postauth_verified_event)

    def test_email_not_verified(self, postauth_not_verified_event):
        assert not postauth.check_email_verified(postauth_not_verified_event)

    def test_email_verified_attribute_missing(self, postauth_not_verified_event):
        postauth_not_verified_event['request']['userAttributes'] = None

        with pytest.raises(Exception) as e:
            assert postauth.check_email_verified(postauth_not_verified_event)
        assert str(e.value) == "Could not get email_verified attribute.", "Exception was not as expected."


@mock_cognitoidp
class TestCognitoActions:
    @pytest.mark.skip(reason="The admin_update_user_attributes action has not been implemented")
    def test_set_email_verified(self, cognito_mock, user_pool_id):
        assert postauth.set_email_verified(user_pool_id, 'test.exists@gmail.com')

    def test_set_email_verified_failed(self, cognito_mock, user_pool_id):
        with pytest.raises(Exception) as e:
            assert postauth.set_email_verified(user_pool_id, 'test.exists@gmail.com')
        assert str(e.value) == "Could not update email_verified attribute.", "Exception was not as expected."
