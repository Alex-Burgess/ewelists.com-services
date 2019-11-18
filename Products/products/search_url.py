import json
import os
import re
import boto3
import logging
from products import common
from urllib.parse import unquote

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


dynamodb = boto3.client('dynamodb')


def handler(event, context):
    response = search_main(event)
    return response


def search_main(event):
    try:
        table_name = common.get_table_name(os.environ)
        index_name = common.get_table_index(os.environ)
        product_url = get_url(event)
        parsed_url = parse_url(product_url)
        product = url_query(table_name, index_name, parsed_url)
    except Exception as e:
        logger.error("Exception: {}".format(e))
        response = common.create_response(500, json.dumps({'error': str(e)}))
        logger.info("Returning response: {}".format(response))
        return response

    data = {'product': product}
    response = common.create_response(200, json.dumps(data))
    return response


def get_url(event):
    try:
        url = event['pathParameters']['url']
        logger.info("Encoded URL: " + url)
    except Exception:
        logger.error("API Event did not contain a Url in the path parameters.")
        raise Exception('API Event did not contain a Url in the path parameters.')

    url = unquote(url)
    logger.info("Decoded URL: " + url)

    return url


def url_query(table_name, index_name, url):
    logger.info("Querying table for product with url {}.".format(url))

    try:
        response = dynamodb.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression="productUrl = :u",
            ExpressionAttributeValues={":u":  {'S': url}}
        )
    except Exception as e:
        logger.info("get item response: " + json.dumps(e.response))
        raise Exception("Unexpected error when searching for product.")

    logger.info("Response: " + json.dumps(response))

    if len(response['Items']) == 0:
        logger.info("No query results for url {}.".format(url))
        return {}

    product = {}

    product['productId'] = response['Items'][0]['productId']['S']
    product['brand'] = response['Items'][0]['brand']['S']
    product['details'] = response['Items'][0]['details']['S']
    product['imageUrl'] = response['Items'][0]['imageUrl']['S']
    product['productUrl'] = response['Items'][0]['productUrl']['S']

    return product


def parse_url(url):
    logger.info("Parsing URL: " + url)

    try:
        # General -  Chop off anything after and including ?
        url = url.split('?')[0]

        # Amazon
        if 'www.amazon.co.uk' in url:
            # Get product code of /dp/ABCDEFGHIJ
            p = re.compile('https://www.amazon.co.uk.*(/dp/[A-Z0-9]{10}).*')
            product_code = p.search(url)
            product_code = product_code.group(1)
            url = 'https://www.amazon.co.uk' + product_code
    except Exception as e:
        logger.info("There was an issue parsing the url: " + str(e))
        return url

    logger.info("Parsed URL: " + url)
    return url
