# A collection of methods that are common across all modules.
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


def create_response(code, body):
    logger.info("Creating response with status code ({}) and body ({})".format(code, body))
    response = {'statusCode': code,
                'body': body,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                }}
    return response


def get_table_name(osenv):
    try:
        table_name = osenv['TABLE_NAME']
        logger.info("TABLE_NAME environment variable value: " + table_name)
    except KeyError:
        logger.error('TABLE_NAME environment variable not set correctly.')
        raise Exception('TABLE_NAME environment variable not set correctly.')

    return table_name


def get_table_index(osenv):
    try:
        index_name = osenv['INDEX_NAME']
        logger.info("INDEX_NAME environment variable value: " + index_name)
    except KeyError:
        logger.error('INDEX_NAME environment variable not set correctly.')
        raise Exception('INDEX_NAME environment variable not set correctly.')

    return index_name


def get_product_id(event):
    try:
        product_id = event['pathParameters']['id']
        logger.info("Product ID: " + product_id)
    except Exception:
        logger.error("API Event did not contain a Product ID in the path parameters.")
        raise Exception('API Event did not contain a Product ID in the path parameters.')

    return product_id
