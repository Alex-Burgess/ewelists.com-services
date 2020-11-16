import os
from lists import common_kpi, logger

log = logger.setup_test_logger()

response = {
    "json": {"status": "ok", "message": "Data pushed"}
}


class TestPost:
    def test_successful_post(self, monkeypatch, api_create_event, requests_mock):
        requests_mock.post('https://app.cyfe.com/api/push/5eb26ce43ea308704280926221234', text='{"status": "ok", "message": "Data pushed"}')
        monkeypatch.setitem(os.environ, 'KPI_URL', 'https://app.cyfe.com/api/push/5eb26ce43ea308704280926221234')
        assert common_kpi.post(os.environ, api_create_event, 'New Lists'), "Post to cyfe failed."

    def test_no_url(self, monkeypatch, api_create_event):
        monkeypatch.setitem(os.environ, 'TEST', 'blah')
        assert not common_kpi.post(os.environ, api_create_event, 'New Lists'), "No post was made."

    def test_bad_url(self, monkeypatch, api_create_event):
        monkeypatch.setitem(os.environ, 'KPI_URL', 'https://app.cyfe.com/api/push/12345')
        assert not common_kpi.post(os.environ, api_create_event, 'New Lists'), "Post to cyfe failed."

    def test_as_postman(self, monkeypatch, api_postman_event):
        monkeypatch.setitem(os.environ, 'KPI_URL', 'https://app.cyfe.com/api/push/5eb26ce43ea308704280926221234')
        assert not common_kpi.post(os.environ, api_postman_event, 'New Lists'), "Post to cyfe failed."

    def test_as_cypress(self, monkeypatch, api_cypress_event):
        monkeypatch.setitem(os.environ, 'KPI_URL', 'https://app.cyfe.com/api/push/5eb26ce43ea308704280926221234')
        assert not common_kpi.post(os.environ, api_cypress_event, 'New Lists'), "Post to cyfe failed."

    def test_with_non_api_event(self, monkeypatch, signup_with_u_and_p_event):
        monkeypatch.setitem(os.environ, 'KPI_URL', 'https://app.cyfe.com/api/push/5eb26ce43ea308704280926221234')
        assert not common_kpi.post(os.environ, signup_with_u_and_p_event, 'New Lists'), "Post to cyfe failed."


class TestPostRequest:
    def test_successful_request(self, requests_mock):
        requests_mock.post('https://app.cyfe.com/api/push/5eb26ce43ea308704280926221234', text='{"status": "ok", "message": "Data pushed"}')

        url = 'https://app.cyfe.com/api/push/5eb26ce43ea308704280926221234'
        data = {
          "data":  [{"Date": "20200506", "New Lists":  "1"}],
          "cumulative": {"New Lists":  "0"},
          "color":  {"New Lists":  "#52ff7f"},
          "type":  {"New Lists":  "line"}
        }
        result = common_kpi.post_request(url, data)
        assert result, "Request did not succeed."

    def test_no_data(self):
        url = 'https://app.cyfe.com/api/push/5eb26ce43ea308704280926228485'
        data = {}
        result = common_kpi.post_request(url, data)
        assert not result, "Request should fail."

    def test_no_url(self):
        url = ''
        data = {
          "data":  [{"Date": "20200506", "New Lists":  "1"}],
          "cumulative": {"New Lists":  "0"},
          "color":  {"New Lists":  "#52ff7f"},
          "type":  {"New Lists":  "line"}
        }
        result = common_kpi.post_request(url, data)
        assert not result, "Request did not succeed."

    def test_bad_url(self):
        url = 'https://app.cyfe.com/api/push/1234'
        data = {
          "data":  [{"Date": "20200506", "New Lists":  "1"}],
          "cumulative": {"New Lists":  "0"},
          "color":  {"New Lists":  "#52ff7f"},
          "type":  {"New Lists":  "line"}
        }
        result = common_kpi.post_request(url, data)
        assert not result, "Request did not succeed."


class TestIsTestUser:
    def test_is_not_postman(self, api_create_event):
        assert not common_kpi.is_postman(api_create_event), "Event should not be a postman event."

    def test_is_postman(self, api_postman_event):
        assert common_kpi.is_postman(api_postman_event), "Event should be a postman event."

    def test_is_not_cypress(self, api_create_event):
        assert not common_kpi.is_cypress(api_create_event), "Event should not be a cypress event."

    def test_is_cypress(self, api_cypress_event):
        assert common_kpi.is_cypress(api_cypress_event), "Event should be a cypress event."


class TestGetUrl:
    def test_get_url(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'KPI_URL', 'https://app.cyfe.com/api/push/5eb26ce43ea308704280926228485')
        url = common_kpi.get_url(os.environ, 'KPI_URL')
        assert url == "https://app.cyfe.com/api/push/5eb26ce43ea308704280926228485", "Url was not as expected."

    def test_get_with_variable_not_set(self):
        url = common_kpi.get_url(os.environ, 'KPI_URL')
        assert url == "", "Url was not empty."


class TestGetColour:
    def test_with_variable(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'KPI_COLOUR', '#52ff7f')
        colour = common_kpi.get_colour(os.environ, 'KPI_COLOUR')
        assert colour == "#52ff7f", "Colour was not as expected."

    def test_without_variable(self):
        colour = common_kpi.get_colour(os.environ, 'KPI_COLOUR')
        assert colour == "#000000", "Colour was not default colour."


class TestGetType:
    def test_with_variable(self, monkeypatch):
        monkeypatch.setitem(os.environ, 'KPI_TYPE', 'line')
        colour = common_kpi.get_type(os.environ, 'KPI_TYPE')
        assert colour == "line", "Type was not as expected."

    def test_without_variable(self):
        colour = common_kpi.get_type(os.environ, 'KPI_TYPE')
        assert colour == "area", "Type was not default colour."


def test_get_date():
    date = common_kpi.get_date()
    assert len(date) == 8, "Date was not todays date in correct format."


class TestCreateJsonData:
    def test_create_data_for_new_lists(self):
        data = common_kpi.create_json_data('New Lists', '20200506', '#52ff7f', 'line')

        expected_data = {
          "data":  [{"Date": "20200506", "New Lists":  "1"}],
          "cumulative": {"New Lists":  "0"},
          "color":  {"New Lists":  "#52ff7f"},
          "type":  {"New Lists":  "line"}
        }

        assert data == expected_data, "Data json was not as expected."

    def test_create_data_for_gifts_added(self):
        data = common_kpi.create_json_data('Gifts Added', '20200506', '#4287f5', 'line')

        expected_data = {
          "data":  [{"Date": "20200506", "Gifts Added":  "1"}],
          "cumulative": {"Gifts Added":  "0"},
          "color":  {"Gifts Added":  "#4287f5"},
          "type":  {"Gifts Added":  "line"}
        }

        assert data == expected_data, "Data json was not as expected."
