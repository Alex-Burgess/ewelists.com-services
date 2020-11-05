import pytest
import os
import re
import json
from lists import get_list, logger

log = logger.setup_test_logger()


@pytest.fixture()
def list_query_response():
    response = [
        {'PK': {'S': 'LIST#12345678-list-0001-1234-abcdefghijkl'}, 'SK': {'S': 'USER#12345678-user-0001-1234-abcdefghijkl'}, 'userId': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'title': {'S': "Child User1 1st Birthday"}, 'occasion': {'S': 'Birthday'}, 'listId': {'S': '12345678-list-0001-1234-abcdefghijkl'}, 'listOwner': {'S': '12345678-user-0001-1234-abcdefghijkl'}, 'createdAt': {'S': '2018-09-01T10:00:00'}, 'description': {'S': 'A gift list for Child User1 birthday.'}, 'eventDate': {'S': '31 October 2018'}, 'imageUrl': {'S': '/images/celebration-default.jpg'}, 'state': {'S': 'open'}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0001-1234-abcdefghijkl"}, "quantity": {"N": "2"}, "reserved": {"N": "1"}, "purchased": {"N": "0"}, "type": {"S": "products"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-prod-0002-1234-abcdefghijkl"}, "quantity": {"N": "3"}, "reserved": {"N": "1"}, "purchased": {"N": "0"}, "type": {"S": "products"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "PRODUCT#12345678-notf-0010-1234-abcdefghijkl"}, "quantity": {"N": "2"}, "reserved": {"N": "0"}, "purchased": {"N": "0"}, "type": {"S": "notfound"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVATION#12345678-prod-0001-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0001-1234-abcdefghijkl"}, "reservationId": {"S": "12345678-resv-0001-1234-abcdefghijkl"}, "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"}, "listOwnerId": {"S": "12345678-user-0001-1234-abcdefghijkl"}, "listTitle": {"S": "Child User1 1st Birthday"}, "name": {"S": "Test User2"}, "email": {"S": "test.user2@gmail.com"}, "productId": {"S": "12345678-prod-0001-1234-abcdefghijkl"}, "productType": {"S": "products"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "reservedAt": {"N": "1573739584"}, "state": {"S": "reserved"}},
        {"PK": {"S": "LIST#12345678-list-0001-1234-abcdefghijkl"}, "SK": {"S": "RESERVATION#12345678-prod-0002-1234-abcdefghijkl#12345678-user-0002-1234-abcdefghijkl#12345678-resv-0002-1234-abcdefghijkl"}, "reservationId": {"S": "12345678-resv-0002-1234-abcdefghijkl"}, "listId": {"S": "12345678-list-0001-1234-abcdefghijkl"}, "listOwnerId": {"S": "12345678-user-0001-1234-abcdefghijkl"}, "listTitle": {"S": "Child User1 1st Birthday"}, "name": {"S": "Test User2"}, "email": {"S": "test.user2@gmail.com"}, "productId": {"S": "12345678-prod-0002-1234-abcdefghijkl"}, "productType": {"S": "products"}, "userId": {"S": "12345678-user-0002-1234-abcdefghijkl"}, "quantity": {"N": "1"}, "reservedAt": {"N": "1573739584"}, "state": {"S": "reserved"}}
    ]

    return response


class TestGenerateListObject:
    def test_generate_list_object(self, list_query_response):
        items = get_list.generate_list_object(list_query_response)
        assert items['list']['listId'] == "12345678-list-0001-1234-abcdefghijkl", "ListId was incorrect."
        assert items['list']['title'] == "Child User1 1st Birthday", "List title was incorrect."
        assert items['list']['description'] == "A gift list for Child User1 birthday.", "List description was incorrect."
        assert items['list']['occasion'] == "Birthday", "List occasion was incorrect."

        assert len(items['products']) == 3, "Number of products was not 2."
        assert items['products']["12345678-prod-0001-1234-abcdefghijkl"] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "quantity": 2, "reserved": 1, "purchased": 0, "type": "products"}, "Product object not correct."
        assert items['products']["12345678-prod-0002-1234-abcdefghijkl"] == {"productId": "12345678-prod-0002-1234-abcdefghijkl", "quantity": 3, "reserved": 1, "purchased": 0, "type": "products"}, "Product object not correct."
        assert items['products']["12345678-notf-0010-1234-abcdefghijkl"] == {"productId": "12345678-notf-0010-1234-abcdefghijkl", "quantity": 2, "reserved": 0, "purchased": 0, "type": "notfound"}, "Product object not correct."

        assert len(items['reserved']) == 2, "Number of products reserved was not 2."
        assert items['reserved'][0] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "name": "Test User2", "email": "test.user2@gmail.com", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "state": "reserved", "reservationId": '12345678-resv-0001-1234-abcdefghijkl', "listId": '12345678-list-0001-1234-abcdefghijkl', "listOwnerId": '12345678-user-0001-1234-abcdefghijkl', "listTitle": 'Child User1 1st Birthday', "productType": 'products'}, "Reserved object not correct."
        assert items['reserved'][1] == {"productId": "12345678-prod-0002-1234-abcdefghijkl", "name": "Test User2", "email": "test.user2@gmail.com", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "state": "reserved", "reservationId": '12345678-resv-0002-1234-abcdefghijkl', "listId": '12345678-list-0001-1234-abcdefghijkl', "listOwnerId": '12345678-user-0001-1234-abcdefghijkl', "listTitle": 'Child User1 1st Birthday', "productType": 'products'}, "Reserved object not correct."


class TestGetListMain:
    def test_get_list_main(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0001-1234-abcdefghijkl", "ListId was not correct."
        assert body['list']['title'] == "Child User1 1st Birthday", "Title was not correct."
        assert body['list']['description'] == "A gift list for Child User1 birthday.", "Description was not correct."
        assert body['list']['eventDate'] == "31 October 2018", "Event data was not correct."
        assert body['list']['occasion'] == "Birthday", "Occasion was not correct."
        assert body['list']['imageUrl'] == "/images/celebration-default.jpg", "Image url was not correct."

        assert len(body['products']) == 6, "Get list response did not contain correct number of products."
        assert body['products']["12345678-prod-0001-1234-abcdefghijkl"] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "quantity": 3, "reserved": 2, "purchased": 0, "type": "products"}, "Product object not correct."
        assert body['products']["12345678-prod-0002-1234-abcdefghijkl"] == {"productId": "12345678-prod-0002-1234-abcdefghijkl", "quantity": 1, "reserved": 0, "purchased": 0, "type": "products", "notes": "I would like size medium."}, "Product object not correct."
        assert body['products']["12345678-prod-0003-1234-abcdefghijkl"] == {"productId": "12345678-prod-0003-1234-abcdefghijkl", "quantity": 1, "reserved": 1, "purchased": 0, "type": "products"}, "Product object not correct."
        assert body['products']["12345678-prod-0004-1234-abcdefghijkl"] == {"productId": "12345678-prod-0004-1234-abcdefghijkl", "quantity": 1, "reserved": 0, "purchased": 1, "type": "products"}, "Product object not correct."
        assert body['products']["12345678-prod-0005-1234-abcdefghijkl"] == {"productId": "12345678-prod-0005-1234-abcdefghijkl", "quantity": 1, "reserved": 0, "purchased": 1, "type": "products"}, "Product object not correct."
        assert body['products']["12345678-notf-0010-1234-abcdefghijkl"] == {"productId": "12345678-notf-0010-1234-abcdefghijkl", "quantity": 2, "reserved": 1, "purchased": 0, "type": "notfound"}, "Product object not correct."

        assert len(body['reserved']) == 6, "Get list response did not contain correct number of reservations."
        assert body['reserved'][0] == {"productId": "12345678-notf-0010-1234-abcdefghijkl", "name": "Test User2", "email": "test.user2@gmail.com", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "state": "reserved", "reservationId": '12345678-resv-0004-1234-abcdefghijkl', "listId": '12345678-list-0001-1234-abcdefghijkl', "listOwnerId": '12345678-user-0001-1234-abcdefghijkl', "listTitle": 'Child User1 1st Birthday', "productType": 'notfound'}, "Reserved object not correct."
        assert body['reserved'][1] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "name": "Test User2", "email": "test.user2@gmail.com", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "state": "reserved", "reservationId": '12345678-resv-0001-1234-abcdefghijkl', "listId": '12345678-list-0001-1234-abcdefghijkl', "listOwnerId": '12345678-user-0001-1234-abcdefghijkl', "listTitle": 'Child User1 1st Birthday', "productType": 'products'}, "Reserved object not correct."
        assert body['reserved'][2] == {"productId": "12345678-prod-0001-1234-abcdefghijkl", "name": "Test User3", "email": "test.user3@gmail.com", "userId": "12345678-user-0003-1234-abcdefghijkl", "quantity": 1, "state": "reserved", "reservationId": '12345678-resv-0002-1234-abcdefghijkl', "listId": '12345678-list-0001-1234-abcdefghijkl', "listOwnerId": '12345678-user-0001-1234-abcdefghijkl', "listTitle": 'Child User1 1st Birthday', "productType": 'products'}, "Reserved object not correct."
        assert body['reserved'][3] == {"productId": "12345678-prod-0003-1234-abcdefghijkl", "name": "Test User99", "email": "test.user99@gmail.com", "userId": "test.user99@gmail.com", "quantity": 1, "state": "reserved", "reservationId": '12345678-resv-0003-1234-abcdefghijkl', "listId": '12345678-list-0001-1234-abcdefghijkl', "listOwnerId": '12345678-user-0001-1234-abcdefghijkl', "listTitle": 'Child User1 1st Birthday', "productType": 'products'}, "Reserved object not correct."
        assert body['reserved'][4] == {"productId": "12345678-prod-0004-1234-abcdefghijkl", "name": "Test User2", "email": "test.user2@gmail.com", "userId": "12345678-user-0002-1234-abcdefghijkl", "quantity": 1, "state": "purchased", "reservationId": '12345678-resv-0006-1234-abcdefghijkl', "listId": '12345678-list-0001-1234-abcdefghijkl', "listOwnerId": '12345678-user-0001-1234-abcdefghijkl', "listTitle": 'Child User1 1st Birthday', "productType": 'products'}, "Reserved object not correct."
        assert body['reserved'][5] == {"productId": "12345678-prod-0005-1234-abcdefghijkl", "name": "Test User99", "email": "test.user99@gmail.com", "userId": "test.user99@gmail.com", "quantity": 1, "state": "purchased", "reservationId": '12345678-resv-0007-1234-abcdefghijkl', "listId": '12345678-list-0001-1234-abcdefghijkl', "listOwnerId": '12345678-user-0001-1234-abcdefghijkl', "listTitle": 'Child User1 1st Birthday', "productType": 'products'}, "Reserved object not correct."

    def test_get_list_with_no_date(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_get_list_event['pathParameters']['id'] = "12345678-list-0002-1234-abcdefghijkl"

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['list']['listId'] == "12345678-list-0002-1234-abcdefghijkl", "Get list response did not contain a listId."
        assert 'eventDate' not in body['list'], "List date was not empty."
        assert body['list']['occasion'] == "Christmas", "Get list response did not contain an occasion."

    def test_get_list_main_wrong_table(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittes')

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == 'Unexpected error when getting list items from table.', "Get list response did not contain the correct error message."

    def test_get_list_that_requestor_does_not_own(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_get_list_event['pathParameters']['id'] = "12345678-list-0004-1234-abcdefghijkl"

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == "User 12345678-user-0001-1234-abcdefghijkl was not owner of List 12345678-list-0004-1234-abcdefghijkl.", "Get list response did not contain the correct error message."

    def test_get_list_that_does_not_exist(self, monkeypatch, api_gateway_get_list_event, dynamodb_mock):
        monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
        api_gateway_get_list_event['pathParameters']['id'] = "12345678-list-0010-1234-abcdefghijkl"

        response = get_list.get_list_main(api_gateway_get_list_event)
        body = json.loads(response['body'])

        assert body['error'] == "List 12345678-list-0010-1234-abcdefghijkl does not exist.", "Get list response did not contain the correct error message."


def test_handler(api_gateway_get_list_event, monkeypatch, dynamodb_mock):
    monkeypatch.setitem(os.environ, 'TABLE_NAME', 'lists-unittest')
    response = get_list.handler(api_gateway_get_list_event, None)
    assert response['statusCode'] == 200
    assert response['headers'] == {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}
    assert re.match('{"list": .*}', response['body'])
