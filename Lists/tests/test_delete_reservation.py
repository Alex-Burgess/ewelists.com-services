import pytest
import os
import json
from lists import delete_reservation, logger

log = logger.setup_logger()


@pytest.fixture
def env_vars(monkeypatch):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    monkeypatch.setitem(os.environ, 'RESERVATIONID_INDEX', 'reservationId-index')


class TestDeleteReservationItem:
    def test_delete_item(self, dynamodb_mock):
        key = {
            'PK': {'S': "LIST#12345678-list-0001-1234-abcdefghijkl"},
            'SK': {'S': "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"}
        }

        result = delete_reservation.delete_reservation_item('lists-unittest', key)
        assert result, "Reservation was not deleted from table."

    def test_delete_with_no_table(self, dynamodb_mock):
        id = '12345678-resv-0001-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete_reservation.delete_reservation_item('missing', id)
        assert str(e.value) == "Reservation item could not be deleted.", "Exception not as expected."

    def test_delete_non_existent__item(self, dynamodb_mock):
        id = '12345678-resv-miss-1234-abcdefghijkl'

        with pytest.raises(Exception) as e:
            delete_reservation.delete_reservation_item('lists-unittest', id)
        assert str(e.value) == "Reservation item could not be deleted.", "Exception not as expected."


class TestDeleteMain:
    def test_delete_main(self, env_vars, api_delete_reservation_event, dynamodb_mock):
        response = delete_reservation.delete_main(api_delete_reservation_event)
        body = json.loads(response['body'])
        assert body['deleted'], "Attribute was not correct."

    def test_reservation_does_not_exist(self, env_vars, api_delete_reservation_event, dynamodb_mock):
        api_delete_reservation_event['pathParameters']['id'] = "12345678-miss-0001-1234-abcdefghijkl"

        response = delete_reservation.delete_main(api_delete_reservation_event)
        body = json.loads(response['body'])
        assert body['error'] == "Reservation ID does not exist.", "Error was not correct."

    def test_reservation_id_is_null(self, env_vars, api_delete_reservation_event, dynamodb_mock):
        api_delete_reservation_event['pathParameters']['id'] = "null"

        response = delete_reservation.delete_main(api_delete_reservation_event)
        body = json.loads(response['body'])
        assert body['error'] == "Path contained a null id parameter.", "Error was not correct."


def test_handler(api_delete_reservation_event, env_vars, dynamodb_mock):
    response = delete_reservation.handler(api_delete_reservation_event, None)
    body = json.loads(response['body'])

    assert response['statusCode'] == 200, "Response statusCode was not as expected."
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, "Response headers were not as expected."
    assert body['deleted'], "Response body was not as expected."
