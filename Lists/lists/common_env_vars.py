import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
if logger.handlers:
    handler = logger.handlers[0]
    handler.setFormatter(logging.Formatter("[%(levelname)s]\t%(asctime)s.%(msecs)dZ\t%(aws_request_id)s\t%(module)s:%(funcName)s\t%(message)s\n", "%Y-%m-%dT%H:%M:%S"))


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


def get_userpool_id(osenv):
    try:
        userpool_id = osenv['USERPOOL_ID']
        logger.info("USERPOOL_ID environment variable value: " + userpool_id)
    except KeyError:
        logger.error('USERPOOL_ID environment variable not set correctly.')
        raise Exception('USERPOOL_ID environment variable not set correctly.')

    return userpool_id


def get_postman_identity(osenv):
    try:
        os_identity = osenv['POSTMAN_USERPOOL_SUB']
    except KeyError:
        logger.error('POSTMAN_USERPOOL_SUB environment variables not set correctly.')
        raise Exception('POSTMAN_USERPOOL_SUB environment variables not set correctly.')

    return os_identity


def get_url(osenv):
    try:
        table_name = osenv['TABLE_NAME']
        logger.info("TABLE_NAME environment variable value: " + table_name)
    except KeyError:
        logger.error('TABLE_NAME environment variable not set correctly.')
        raise Exception('TABLE_NAME environment variable not set correctly.')

    environment = table_name.split('-')[-1]

    if environment == 'prod':
        url = 'https://ewelists.com'
    elif environment == 'staging':
        url = 'https://staging.ewelists.com'
    else:
        url = 'https://test.ewelists.com'

    return url
