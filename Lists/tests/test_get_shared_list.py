import pytest
import os
import re
import json
from lists import get_shared_list, logger

log = logger.setup_logger()


@pytest.fixture()
def list_query_response():
    response = [
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}, 'state': {'S': 'open'}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "quantity": {"N": "2"}, "reserved": {"N": "1"}, "purchased": {"N": "0"}, "type": {"S": "products"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0002-1234-abcdefghijkl"}, "quantity": {"N": "3"}, "reserved": {"N": "1"}, "purchased": {"N": "0"}, "type": {"S": "products"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-notf-0010-1234-abcdefghijkl"}, "quantity": {"N": "2"}, "reserved": {"N": "0"}, "purchased": {"N": "0"}, "type": {"S": "notfound"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"}, "reservationId": {"S": "12345678-resv-0001-1234-abcdefghijkl"}, "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"}, "listTitle": {"S": "Child User1 1st Birthday"}, "name": {"S": "Test User2"}, "email": {"S": "test.user2@gmail.com"}, "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"}, "productType": {"S": "products"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "reservedAt": {"N": "1573739584"}, "state": {"S": "reserved"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVATION#12345678-prod-0002-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0002-1234-abcdefghijkl"}, "reservationId": {"S": "12345678-resv-0002-1234-abcdefghijkl"}, "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"}, "listTitle": {"S": "Child User1 1st Birthday"}, "name": {"S": "Test User2"}, "email": {"S": "test.user2@gmail.com"}, "productId": {"S": "12345678-prod-0002-1234-abcdefghijkl"}, "productType": {"S": "products"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "reservedAt": {"N": "1573739584"}, "state": {"S": "reserved"}}
    ]

    return response


class TestGetListQuery:
    def test_get_list_query(self, dynamodb_mock):
        list_id = "12345678-list-0001-1234-abcdefghijkl"
        items = get_shared_list.get_list_query('lists-unittest', list_id)
        assert len(items) == 14, "Number of items deleted was not as expected."

    def test_get_list_query_no_table_name(self, dynamodb_mock):
        list_id = "12345678-list-0001-1234-abcdefghijkl"

        with pytest.raises(Exception) as e:
            get_shared_list.get_list_query('lists-unittes', list_id)
        assert str(e.value) == "Unexpected error when getting list item from table.", "Exception not as expected."

    def test_get_list_query_for_item_that_does_not_exist(self, dynamodb_mock):
        list_id = "12345678-list-0009-1234-abcdefghijkl"

        with pytest.raises(Exception) as e:
            get_shared_list.get_list_query('lists-unittest', list_id)
        assert str(e.value) == "No results for List ID 12345678-list-0009-1234-abcdefghijkl.", "Exception not as expected."


class TestGenerateListObject:
    def test_generate_list_object(self, list_query_response):
        items = get_shared_list.generate_list_object(list_query_response)
        assert items['list']['listId'] == "12345678-list-0001-1234-abcdefghijkl", "ListId was incorrect."
        assert items['list']['title'] == "Child User1 1st Birthday", "List title was incorrect."
        assert items['list']['description'] == "A gift list for Child User1 birthday.", "List description was incorrect."
        assert items['list']['occasion'] == "Birthday", "List occasion was incorrect."
        assert items['list']['state'] == "open", "List state was incorrect."

        assert len(items['products']) == 3, "Number of products was not 2."
        assert items['products']["12345678-prod-0001-1234-abcdefghijkl"] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "quantity": 2, "reserved": 1, "purchased": 0, "type": "products"}, "Product object not correct."
        assert items['products']["12345678-prod-0002-1234-abcdefghijkl"] == {"productId": "12345678-prod-0002-1234-abcdefghijkl", "quantity": 3, "reserved": 1, "purchased": 0, "type": "products"}, "Product object not correct."
        assert items['products']["12345678-notf-0010-1234-abcdefghijkl"] == {"productId": "12345678-notf-0010-1234-abcdefghijkl", "quantity": 2, "reserved": 0, "purchased": 0, "type": "notfound"}, "Product object not correct."

        assert len(items['reserved']) == 2, "Number of products reserved was not 2."
        assert len(items['reserved']["12345678-prod-0001-1234-abcdefghijkl"]) == 1, "Number of users that have reserved product not correct."
        assert len(items['reserved']["12345678-prod-0002-1234-abcdefghijkl"]) == 1, "Number of users that have reserved product not correct."
        assert items['reserved']["12345678-prod-0001-1234-abcdefghijkl"]['12345678-user-0002-1234-abcdefghijkl'] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "name": "Test User2", "email": "test.user2@gmail.com", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "state": "reserved", "reservationId": '12345678-resv-0001-1234-abcdefghijkl', "listId": '12345678-list-0001-1234-abcdefghijkl', "listTitle": 'Child User1 1st Birthday', "productType": 'products'}, "Reserved object not correct."
        assert items['reserved']["12345678-prod-0002-1234-abcdefghijkl"]['12345678-user-0002-1234-abcdefghijkl'] == {"productId": "12345678-prod-0002-1234-abcdefghijkl", "name": "Test User2", "email": "test.user2@gmail.com", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "state": "reserved", "reservationId": '12345678-resv-0002-1234-abcdefghijkl', "listId": '12345678-list-0001-1234-abcdefghijkl', "listTitle": 'Child User1 1st Birthday', "productType": 'products'}, "Reserved object not correct."


class TestGetSharedListMain:
    def test_get_shared_list_main(self, monkeypatch, api_get_shared_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = get_shared_list.get_shared_list_main(api_get_shared_list_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0001-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert body['list']['title'] == "Child User1 1st Birthday", "Get list response did not contain a title."
        assert body['list']['description'] == "A gift list for Child User1 birthday.", "Get list response did not contain a description."
        assert body['list']['eventDate'] == "31 October 2018", "Get list response did not contain a date."
        assert body['list']['occasion'] == "Birthday", "Get list response did not contain an occasion."
        assert body['list']['imageUrl'] == "/images/celebration-default.jpg", "Get list response did not contain an imageUrl."
        assert body['list']['state'] == "open", "List state was incorrect."

        p = body['products']
        assert len(p) == 6, "Get list response did not contain correct number of products."
        assert p["12345678-prod-0001-1234-abcdefghijkl"] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "quantity": 3, "reserved": 2, "purchased": 0, "type": "products"}, "Product object not correct."
        assert p["12345678-prod-0002-1234-abcdefghijkl"] == {"productId": "12345678-prod-0002-1234-abcdefghijkl", "quantity": 1, "reserved": 0, "purchased": 0, "type": "products"}, "Product object not correct."
        assert p["12345678-prod-0003-1234-abcdefghijkl"] == {"productId": "12345678-prod-0003-1234-abcdefghijkl", "quantity": 1, "reserved": 1, "purchased": 0, "type": "products"}, "Product object not correct."
        assert p["12345678-notf-0010-1234-abcdefghijkl"] == {"productId": "12345678-notf-0010-1234-abcdefghijkl", "quantity": 2, "reserved": 1, "purchased": 0, "type": "notfound"}, "Product object not correct."
        assert p["12345678-prod-0004-1234-abcdefghijkl"] == {"productId": "12345678-prod-0004-1234-abcdefghijkl", "quantity": 1, "reserved": 0, "purchased": 1, "type": "products"}, "Product object not correct."
        assert p["12345678-prod-0005-1234-abcdefghijkl"] == {"productId": "12345678-prod-0005-1234-abcdefghijkl", "quantity": 1, "reserved": 0, "purchased": 1, "type": "products"}, "Product object not correct."

        expected_reservation = {
            "12345678-notf-0010-1234-abcdefghijkl": {
                "12345678-user-0002-1234-abcdefghijkl": {
                    "reservationId": "12345678-resv-0004-1234-abcdefghijkl", "productId": "12345678-notf-0010-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "listId": "12345678-list-0001-1234-abcdefghijkl", "name": "Test User2", "email": "test.user2@gmail.com", "quantity": 1, "state": "reserved", "listTitle": "Child User1 1st Birthday", "productType": "notfound"
                }
            },
            "12345678-prod-0001-1234-abcdefghijkl": {
                "12345678-user-0002-1234-abcdefghijkl": {
                    "reservationId": "12345678-resv-0001-1234-abcdefghijkl", "productId": "12345678-prod-0001-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "listId": "12345678-list-0001-1234-abcdefghijkl", "name": "Test User2", "email": "test.user2@gmail.com", "quantity": 1, "state": "reserved", "listTitle": "Child User1 1st Birthday", "productType": "products"
                },
                "12345678-user-0003-1234-abcdefghijkl": {
                    "reservationId": "12345678-resv-0002-1234-abcdefghijkl", "productId": "12345678-prod-0001-1234-abcdefghijkl", "userId": "12345678-user-0003-1234-abcdefghijkl", "listId": "12345678-list-0001-1234-abcdefghijkl", "name": "Test User3", "email": "test.user3@gmail.com", "quantity": 1, "state": "reserved", "listTitle": "Child User1 1st Birthday", "productType": "products"
                }
            },
            "12345678-prod-0003-1234-abcdefghijkl": {
                "test.user99@gmail.com": {
                    "reservationId": "12345678-resv-0003-1234-abcdefghijkl", "productId": "12345678-prod-0003-1234-abcdefghijkl", "userId": "test.user99@gmail.com", "listId": "12345678-list-0001-1234-abcdefghijkl", "name": "Test User99", "email": "test.user99@gmail.com", "quantity": 1, "state": "reserved", "listTitle": "Child User1 1st Birthday", "productType": "products"
                }
            },
            "12345678-prod-0004-1234-abcdefghijkl": {
                "12345678-user-0002-1234-abcdefghijkl": {
                    "reservationId": "12345678-resv-0006-1234-abcdefghijkl", "productId": "12345678-prod-0004-1234-abcdefghijkl", "userId": "12345678-user-0002-1234-abcdefghijkl", "listId": "12345678-list-0001-1234-abcdefghijkl", "name": "Test User2", "email": "test.user2@gmail.com", "quantity": 1, "state": "purchased", "listTitle": "Child User1 1st Birthday", "productType": "products"
                }
            },
            "12345678-prod-0005-1234-abcdefghijkl": {
                "test.user99@gmail.com": {
                    "reservationId": "12345678-resv-0007-1234-abcdefghijkl", "productId": "12345678-prod-0005-1234-abcdefghijkl", "userId": "test.user99@gmail.com", "listId": "12345678-list-0001-1234-abcdefghijkl", "name": "Test User99", "email": "test.user99@gmail.com", "quantity": 1, "state": "purchased", "listTitle": "Child User1 1st Birthday", "productType": "products"
                }
            }
        }

        assert body['reserved'] == expected_reservation

    def test_get_shared_list_with_no_date(self, monkeypatch, api_get_shared_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_get_shared_list_event['pathParameters']['id'] = "12345678-list-0002-1234-abcdefghijkl"

        response = get_shared_list.get_shared_list_main(api_get_shared_list_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0002-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert 'eventDate' not in body['list'], "List date was not empty."
        assert body['list']['occasion'] == "Christmas", "Get list response did not contain an occasion."

    def test_get_shared_list_main_no_table(self, monkeypatch, api_get_shared_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = get_shared_list.get_shared_list_main(api_get_shared_list_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting list item from table.', "Get list response did not contain the correct error message."

    def test_get_shared_list_with_authenticated_user(self, monkeypatch, api_get_shared_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_get_shared_list_event['requestContext']['identity']['cognitoAuthenticationProvider'] = "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0003-1234-abcdefghijkl"

        response = get_shared_list.get_shared_list_main(api_get_shared_list_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0001-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert len(body['products']) == 6, "Get list response did not contain correct number of products."
        assert len(body['reserved']) == 5, "Number of products reserved was not correct."

    def test_get_shared_list_with_unauthenticated_user(self, monkeypatch, api_get_shared_list_unauthed_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = get_shared_list.get_shared_list_main(api_get_shared_list_unauthed_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0001-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert len(body['products']) == 6, "Get list response did not contain correct number of products."
        assert len(body['reserved']) == 5, "Number of products reserved was not correct."


def test_handler(api_get_shared_list_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = get_shared_list.handler(api_get_shared_list_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"list": .*}', response['body'])
