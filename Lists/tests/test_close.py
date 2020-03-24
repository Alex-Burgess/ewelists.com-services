import os
import json
from lists import close, logger

log = logger.setup_logger()


class TestUpdateList:
    def test_update_list(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0001-1234-abcdefghijkl'
        assert close.update_list('lists-unittest', user_id, list_id)

    def test_update_list_already_closed(self, dynamodb_mock):
        user_id = '12345678-user-0001-1234-abcdefghijkl'
        list_id = '12345678-list-0003-1234-abcdefghijkl'
        assert close.update_list('lists-unittest', user_id, list_id)


def test_handler(api_close_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = close.handler(api_close_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}

    body = json.loads(response['body'])
    assert body['closed']
