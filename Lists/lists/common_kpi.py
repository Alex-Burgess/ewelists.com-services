import requests
import json
from datetime import datetime
from lists import logger

log = logger.setup_logger()


def post(osenv, event, name):
    url = get_url(osenv, 'KPI_URL')

    if not url:
        log.info("KPI post skipped, no url provided in environment variable.")
        return False
    elif is_postman(event) or is_cypress(event) or has_test_flag(event):
        log.info("KPI post skipped, request was from postman or cypress.")
        return False

    datestamp = get_date()
    colour = get_colour(osenv, 'KPI_COLOUR')
    type = get_type(osenv, 'KPI_TYPE')
    data = create_json_data(name, datestamp, colour, type)
    result = post_request(url, data)

    if result:
        log.info("KPI post succeeded. name={} url={}.".format(name, url))

    return result


def is_postman(event):
    try:
        userAgent = event['requestContext']['identity']['userAgent']
    except Exception:
        log.info("Event was not an API request.")
        return False

    if 'PostmanRuntime' in userAgent:
        return True

    return False


def is_cypress(event):
    try:
        body = event['body']
    except Exception:
        return False

    if 'Cypress' in body:
        return True

    return False


def has_test_flag(event):
    try:
        body = json.loads(event['body'])
    except Exception:
        return False

    if 'test_flag' in body:
        if body['test_flag']:
            log.info("Test flag: " + str(body['test_flag']))
            return True

    return False


def post_request(url, data):
    try:
        r = requests.post(url, data=json.dumps(data))
    except Exception as e:
        log.error("KPI post failed with exception: {}".format(e))
        return False

    output = json.loads(r.text)

    if output['status'] == 'error':
        log.error("KPI post failed: {}".format(r.json()))
        return False

    return True


def get_url(osenv, name):
    try:
        url = osenv[name]
        log.info(name + " environment variable value: " + url)
    except KeyError:
        log.info(name + " environment variable was not present.")
        url = ''

    return url


def get_colour(osenv, name):
    try:
        colour = osenv[name]
        log.info(name + " environment variable value: " + colour)
    except KeyError:
        log.info(name + " environment variable was not present, using default colour.")
        colour = '#000000'

    return colour


def get_type(osenv, name):
    try:
        type = osenv[name]
        log.info(name + " environment variable value: " + type)
    except KeyError:
        log.info(name + " environment variable was not present, using default type.")
        type = 'area'

    return type


def get_date():
    dateTimeObj = datetime.now()
    return dateTimeObj.strftime("%Y%m%d")


def create_json_data(name, date, colour, type):
    return {
      "data":  [
        {
          "Date":  date,
          name:  "1"
        }
      ],
      "cumulative": {
        name:  "0"
      },
      "color":  {
        name:  colour
      },
      "type":  {
        name:  type
      }
    }
