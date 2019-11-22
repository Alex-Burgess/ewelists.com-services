import pytest
import os
from lists import common_env_vars


class TestGetTableName:
    def test_get_table_name(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-test')
        table_name = common_env_vars.get_table_name(os.environ)
        assert table_name == "lists-test", "Table name from os environment variables was not as expected."

    def test_get_table_name_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common_env_vars.get_table_name(os.environ)
        assert str(e.value) == "TABLE_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetTableIndex:
    def test_get_table_index(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'INDEX_NAME', 'index-test')
        index_name = common_env_vars.get_table_index(os.environ)
        assert index_name == "index-test", "Index name from os environment variables was not as expected."

    def test_get_table_index_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common_env_vars.get_table_index(os.environ)
        assert str(e.value) == "INDEX_NAME environment variable not set correctly.", "Exception not as expected."


class TestGetUserpoolId:
    def test_get_userpool_id(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'USERPOOL_ID', 'ewelists-test')
        userpool_id = common_env_vars.get_userpool_id(os.environ)
        assert userpool_id == "ewelists-test", "Table name from os environment variables was not as expected."

    def test_get_userpool_name_os_var_not_set(self):
        with pytest.raises(Exception) as e:
            common_env_vars.get_userpool_id(os.environ)
        assert str(e.value) == "USERPOOL_ID environment variable not set correctly.", "Exception not as expected."


class TestGetPostmanIdentity:
    def test_get_postman_identity(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'POSTMAN_USERPOOL_SUB', '12345678-user-api1-1234-abcdefghijkl')

        identity = common_env_vars.get_postman_identity(os.environ)
        assert identity == '12345678-user-api1-1234-abcdefghijkl', "POSTMAN_USERPOOL_SUB not as expected."

    def test_get_postman_identity_when_identity_id_missing(self):
        with pytest.raises(Exception) as e:
            common_env_vars.get_postman_identity(os.environ)
        assert str(e.value) == "POSTMAN_USERPOOL_SUB environment variables not set correctly.", "Exception not as expected."


class TestGetUrl:
    def test_with_test_table(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-test')
        url = common_env_vars.get_url(os.environ)
        assert url == "https://test.ewelists.com", "Url was not correct."

    def test_with_staging_table(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-staging')
        url = common_env_vars.get_url(os.environ)
        assert url == "https://staging.ewelists.com", "Url was not correct."

    def test_with_prod_table(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-prod')
        url = common_env_vars.get_url(os.environ)
        assert url == "https://ewelists.com", "Url was not correct."
