import pytest
import boto3
import json
from moto import mock_dynamodb2


@pytest.fixture
def empty_table():
    with mock_dynamodb2():
        table_name = 'products-unittest'

        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'productId', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        yield dynamodb


@pytest.fixture
def table():
    with mock_dynamodb2():
        table_name = 'products-unittest'

        dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')

        table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': 'productId', 'KeyType': 'HASH'}],
                AttributeDefinitions=[
                    {'AttributeName': 'productId', 'AttributeType': 'S'},
                    {'AttributeName': 'productUrl', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'producturl-index',
                        'KeySchema': [{'AttributeName': 'productUrl', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            )

        items = [
            {
                "productId": "12345678-prod-0001-1234-abcdefghijkl",
                "retailer": "amazon.co.uk",
                "brand": "BABYBJÖRN",
                "details": "Travel Cot Easy Go, Anthracite, with transport bag",
                "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
                "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58",
                "price": "100.00"
            },
            {
                "productId": "12345678-prod-0002-1234-abcdefghijkl",
                "brand": "John Lewis & Partners",
                "details": "Baby GOTS Organic Cotton Elephant Sleepsuit, Pack of 3, White",
                "price": "13.00",
                "imageUrl": "https://johnlewis.scene7.com/is/image/JohnLewis/003953444?$rsp-pdp-port-640$",
                "productUrl": "https://www.johnlewis.com/john-lewis-partners-baby-gots-organic-cotton-elephant-sleepsuit-pack-of-3-white/p4233425"
            },
            {
                "productId": "12345678-prod-0003-1234-abcdefghijkl",
                "retailer": "amazon.co.uk",
                "brand": "BABYBJÖRN",
                "details": "Travel Cot Easy Go, Anthracite, with transport bag",
                "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
                "productUrl": "https://www.amazon.co.uk/dp/B01H24LM58"
            },
            {
                "productId": "12345678-prod-0004-1234-abcdefghijkl",
                "retailer": "amazon.co.uk",
                "brand": "BABYBJÖRN",
                "details": "Travel Cot Easy Go, Anthracite, with transport bag",
                "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
                "productUrl": "https://www.amazon.co.uk/dp/B01H24LM12",
                "searchHidden": True
            }
        ]

        for item in items:
            table.put_item(TableName=table_name, Item=item)

        yield


@pytest.fixture
def api_gateway_with_id_event():
    event = api_gateway_base_event()
    event['resource'] = "/products/{id}"
    event['path'] = "/products/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-prod-0001-1234-abcdefghijkl"}
    event['body'] = "null"

    return event


@pytest.fixture
def api_gateway_event_with_no_product_id():
    event = api_gateway_base_event()
    event['resource'] = "/products"
    event['path'] = "/products"
    event['httpMethod'] = "POST"

    return event


@pytest.fixture
def api_create_event():
    event = api_gateway_base_event()
    event['httpMethod'] = "POST"
    event['body'] = "{\n    \"retailer\": \"amazon.co.uk\",\n    \"brand\": \"BABYBJÖRN\",\n    \"details\": \"Travel Cot Easy Go, Anthracite, with transport bag\",\n    \"productUrl\": \"https://www.amazon.co.uk/dp/B01H24LM58\",\n    \"imageUrl\": \"https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg\"\n}"

    return event


@pytest.fixture
def api_create_with_price_event():
    event = api_gateway_base_event()
    event['httpMethod'] = "POST"
    event['body'] = "{\n    \"retailer\": \"amazon.co.uk\",\n    \"price\": \"100.00\",\n    \"brand\": \"BABYBJÖRN\",\n    \"details\": \"Travel Cot Easy Go, Anthracite, with transport bag\",\n    \"productUrl\": \"https://www.amazon.co.uk/dp/B01H24LM58\",\n    \"imageUrl\": \"https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg\"\n}"

    return event


@pytest.fixture
def api_create_with_search_flag_event():
    event = api_gateway_base_event()
    event['httpMethod'] = "POST"

    event['body'] = json.dumps({
        "brand": "BABYBJÖRN",
        "details": "Travel Cot Easy Go, Anthracite, with transport bag",
        "retailer": "amazon.co.uk",
        "imageUrl": "https://images-na.ssl-images-amazon.com/images/I/81qYpf1Sm2L._SX679_.jpg",
        "productUrl": "https://www.amazon.co.uk/dp/B01H24LM12",
        "price": "100.00",
        "searchHidden": True
    })

    return event


@pytest.fixture
def api_gateway_delete_event():
    event = api_gateway_base_event()
    event['resource'] = "/products/{id}"
    event['path'] = "/products/12345678-prod-0010-1234-abcdefghijkl"
    event['httpMethod'] = "DELETE"
    event['pathParameters'] = {"id": "12345678-prod-0010-1234-abcdefghijkl"}

    return event


@pytest.fixture
def api_gateway_get_product_event():
    event = api_gateway_base_event()
    event['resource'] = "/products/{id}"
    event['path'] = "/products/12345678-prod-0001-1234-abcdefghijkl"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"id": "12345678-prod-0001-1234-abcdefghijkl"}
    event['body'] = "null"

    return event


@pytest.fixture
def api_gateway_search_event():
    event = api_gateway_base_event()
    event['resource'] = "/products/url/{url}"
    event['path'] = "/products/url/https%3A%2F%2Fwww.amazon.co.uk%2Fdp%2FB01H24LM58"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"url": "https%3A%2F%2Fwww.amazon.co.uk%2Fdp%2FB01H24LM58"}
    event['body'] = "null"

    return event


def api_gateway_base_event():
    """ Generates API GW Event"""

    return {
        "resource": "/products",
        "path": "/products",
        "httpMethod": "GET",
        "headers": {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Cache-Control": "no-cache",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "GB",
            "Content-Type": "text/plain",
            "Host": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "Postman-Token": "512388b6-c036-4d11-a6c9-adf8e07e1da0",
            "User-Agent": "PostmanRuntime/7.15.2",
            "Via": "1.1 a1cb6e97bccd4899987b343ae5d4c252.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "zJgUVrLX5O4d-B43SVe4Bs6YVpSTWXxrAVtWjeF0FcAnXJ8dARKQRA==",
            "x-amz-content-sha256": "b9d4c66e0ae3c09af8a6ce4c99518f244c3db701a196021c79f094b51e9b49d4",
            "x-amz-date": "20191008T162240Z",
            "X-Amzn-Trace-Id": "Root=1-5d9cb7d0-6965798907570a0728570212",
            "X-Forwarded-For": "5.81.150.55, 70.132.38.104",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "queryStringParameters": "null",
        "multiValueQueryStringParameters": "null",
        "pathParameters": "null",
        "stageVariables": "null",
        "requestContext": {
            "resourceId": "sgzmgr",
            "resourcePath": "/products",
            "httpMethod": "GET",
            "extendedRequestId": "BQGojGkBjoEFsTw=",
            "requestTime": "08/Oct/2019:16:22:40 +0000",
            "path": "/test/products",
            "accountId": "123456789012",
            "protocol": "HTTP/1.1",
            "stage": "test",
            "domainPrefix": "4sdcvv0n2e",
            "requestTimeEpoch": 1570551760227,
            "requestId": "a3d965cd-a79b-4249-867a-a03eb858a839",
            "identity": {
                "cognitoIdentityPoolId": "eu-west-1:2208d797-dfc9-40b4-8029-827c9e76e029",
                "accountId": "123456789012",
                "cognitoIdentityId": "eu-west-1:db9476fd-de77-4977-839f-4f943ff5d68c",
                "caller": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials",
                "sourceIp": "31.49.230.217",
                "principalOrgId": "o-d8jj6dyqv2",
                "accessKey": "ABCDEFGPDMJL4EB35H6H",
                "cognitoAuthenticationType": "authenticated",
                "cognitoAuthenticationProvider": "cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7,cognito-idp.eu-west-1.amazonaws.com/eu-west-1_vqox9Z8q7:CognitoSignIn:12345678-user-0001-1234-abcdefghijkl",
                "userArn": "arn:aws:sts::123456789012:assumed-role/Ewelists-test-CognitoAuthRole/CognitoIdentityCredentials",
                "userAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Mobile Safari/537.36",
                "user": "AROAZUFPDMJL6KJM4LLZI:CognitoIdentityCredentials"
            },
            "domainName": "4sdcvv0n2e.execute-api.eu-west-1.amazonaws.com",
            "apiId": "4sdcvv0n2e"
        },
        "body": "null",
        "isBase64Encoded": "false"
    }


@pytest.fixture
def api_query_metadata_event():
    event = api_gateway_base_event()
    event['resource'] = "/products/query/metadata/{url}"
    event['path'] = "/products/query/metadata/https%3A%2F%2Fwww.thewhitecompany.com%2Fuk%2FSnowman-Knitted-Romper%2Fp%2FSNTOO"
    event['httpMethod'] = "GET"
    event['pathParameters'] = {"url": "https%3A%2F%2Fwww.thewhitecompany.com%2Fuk%2FSnowman-Knitted-Romper%2Fp%2FSNTOO"}

    return event


@pytest.fixture
def metadata_response_wc():
    return {
      "og": {
        "title": "Snowman Knitted Romper | Newborn & Unisex | The  White Company",
        "description": "The perfect Christmas gift, our bestselling cosy knitted bodysuit has adorable pom-poms at the front to mimic a chilly snowman. With fastenings on the shoulder and leg openings, changing baby is easy. The bodysuit is footless with long sleeves and looks even cuter when paired with our novelty Snowman Hat for a complete outfit. Design & Fit \u2022 Long-sleeved romper \u2022 Pom-poms down the front \u2022 Button fastening on shoulder and legs \u2022 Pair with matching hat for full outfit Fabric & Care \u2022 100% cotton \u2022 Machine wash \u2022 Safety warning: keep away from fire See more: Newborn, The Little White Company",
        "image": "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$",
        "image:width": "200",
        "image:height": "200",
        "url": "https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO?swatch=White",
        "type": "product",
        "locale": "en_GB",
        "site_name": "The  White Company UK"
      },
      "meta": {
        "description": "The perfect Christmas gift, our bestselling cosy knitted bodysuit has adorable pom-poms at the front to mimic a chilly snowman. With fastenings on the shoulder and leg openings, changing baby is easy. The bodysuit is footless with long sleeves and looks even cuter when paired with our novelty Snowman Hat for a complete outfit. Design & Fit \u2022 Long-sleeved romper \u2022 Pom-poms down the front \u2022 Button fastening on shoulder and legs \u2022 Pair with matching hat for full outfit Fabric & Care \u2022 100% cotton \u2022 Machine wash \u2022 Safety warning: keep away from fire See more: Newborn, The Little White Company",
        "product:price:amount": "34.0",
        "product:price:currency": "GBP",
        "": [
          "Snowman Knitted Romper | Newborn & Unisex | The  White Company",
          "The perfect Christmas gift, our bestselling cosy knitted bodysuit has adorable pom-poms at the front to mimic a chilly snowman. With fastenings on the shoulder and leg openings, changing baby is easy. The bodysuit is footless with long sleeves and looks even cuter when paired with our novelty Snowman Hat for a complete outfit. Design & Fit \u2022 Long-sleeved romper \u2022 Pom-poms down the front \u2022 Button fastening on shoulder and legs \u2022 Pair with matching hat for full outfit Fabric & Care \u2022 100% cotton \u2022 Machine wash \u2022 Safety warning: keep away from fire See more: Newborn, The Little White Company",
          "https://whitecompany.scene7.com/is/image/whitecompany/Snowman-Knitted-Romper/SNTOO_15_MAIN_P?$D_PDP_412x525$",
          "200",
          "https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO?swatch=White",
          "product",
          "en_GB",
          "The  White Company UK",
          "1851456161814830"
        ]
      },
      "dc": {},
      "page": {
        "title": "Snowman Knitted Romper | Newborn & Unisex | The  White Company UK",
        "canonical": "https://www.thewhitecompany.com/uk/Snowman-Knitted-Romper/p/SNTOO"
      }
    }


@pytest.fixture
def metadata_response_jl():
    return {
      'og': {},
      'meta': {
        'description': 'Buy Aqua Mini Micro Deluxe Scooter, 2-5 years from our Wheeled Toys & Bikes range at John Lewis & Partners. Free Delivery on orders over £50.',
        'og:image': 'https://johnlewis.scene7.com/is/image/JohnLewis/235862595?',
        'og:type': 'product',
        'og:title': 'Mini Micro Deluxe Scooter, 2-5 years, Aqua',
        'og:locale': 'en_GB',
        'og:image:type': 'image/jpeg',
        'og:url': 'https://www.johnlewis.com/mini-micro-deluxe-scooter-2-5-years/aqua/p3567221',
        'og:description': 'Buy Aqua Mini Micro Deluxe Scooter, 2-5 years from our Wheeled Toys & Bikes range at John Lewis & Partners. Free Delivery on orders over £50.',
        'og:site-name': 'John Lewis'
      },
      'dc': {},
      'page': {
        'title': 'Mini Micro Deluxe Scooter, 2-5 years at John Lewis & Partners',
        'canonical': 'https://www.johnlewis.com/mini-micro-deluxe-scooter-2-5-years/p3567221'
      }
    }


@pytest.fixture
def metadata_response_jojo():
    return {
      'og': {
        'type': 'product',
        'title': "Kids' Penguin Towelling Dressing Gown",
        'image': 'https://www.jojomamanbebe.co.uk/media/catalog/product/cache/e8cfbc35dc14c111e189893c9b8f265c/h/1/h1182_e2883.jpg',
        'description': '',
        'url': 'https://www.jojomamanbebe.co.uk/kids-penguin-towelling-robe-h1182.html'
        },
      'meta': {
        'title': "Kids' Penguin Towelling Bath Robe | JoJo Maman Bebe",
        'description': "The Penguin Towelling Dressing Gown is an impossibly cute style that's both practical and fun to wear. Supersoft cotton terry is so cosy, making it useful for chilly mornings and nights. The hooded style makes it extra warm, and little ones will love the", 'keywords': 'JoJo Maman Bebe',
        'og:type': 'product',
        'og:title': "Kids' Penguin Towelling Dressing Gown",
        'og:image': 'https://www.jojomamanbebe.co.uk/media/catalog/product/cache/e8cfbc35dc14c111e189893c9b8f265c/h/1/h1182_e2883.jpg',
        'og:description': '',
        'og:url': 'https://www.jojomamanbebe.co.uk/kids-penguin-towelling-robe-h1182.html',
        'product:price:amount': '18',
        'product:price:currency': 'GBP',
      },
      'dc': {},
      'page': {
        'title': "Kids' Penguin Towelling Bath Robe | JoJo Maman Bebe",
        'canonical': 'https://www.jojomamanbebe.co.uk/kids-penguin-towelling-robe-h1182.html'
      }
    }


@pytest.fixture
def metadata_response_gltc():
    return {
      'og': {
        'site_name': 'Great Little Trading Co.',
        'url': 'https://www.gltc.co.uk/products/woodland-christmas-advent-calendar',
        'title': 'Woodland Christmas Advent Calendar',
        'type': 'product',
        'description': "Designed in the UK, our Woodland Christmas Kids' Advent Calendar is a family heirloom in the making! Check out this wooden kids' advent calendar today at GLTC.",
        'price:amount': '45.00',
        'price:currency': 'GBP',
        'image': [
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_1_1200x1200.png?v=1603200782',
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_2_1200x1200.jpg?v=1603214664',
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_3_1200x1200.jpg?v=1603214599'
        ],
        'image:secure_url': [
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_1_1200x1200.png?v=1603200782',
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_2_1200x1200.jpg?v=1603214664',
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_3_1200x1200.jpg?v=1603214599'
        ]
      },
      'meta': {
        'description': "Designed in the UK, our Woodland Christmas Kids' Advent Calendar is a family heirloom in the making! Check out this wooden kids' advent calendar today at GLTC.", 'og:site_name': 'Great Little Trading Co.',
        'og:url': 'https://www.gltc.co.uk/products/woodland-christmas-advent-calendar',
        'og:title': 'Woodland Christmas Advent Calendar',
        'og:type': 'product',
        'og:description': "Designed in the UK, our Woodland Christmas Kids' Advent Calendar is a family heirloom in the making! Check out this wooden kids' advent calendar today at GLTC.",
        'og:price:amount': '45.00',
        'og:price:currency': 'GBP',
        'og:image': [
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_1_1200x1200.png?v=1603200782',
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_2_1200x1200.jpg?v=1603214664',
          'http://cdn.shopify.com/s/files/1/2341/5115/products/l4978_3_1200x1200.jpg?v=1603214599'
        ],
        'og:image:secure_url': [
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_1_1200x1200.png?v=1603200782',
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_2_1200x1200.jpg?v=1603214664',
          'https://cdn.shopify.com/s/files/1/2341/5115/products/l4978_3_1200x1200.jpg?v=1603214599'
        ]
      },
      'dc': {},
      'page': {
        'title': "Kids' Christmas Advent Calendar | Great Little Trading Co.",
        'canonical': 'https://www.gltc.co.uk/products/woodland-christmas-advent-calendar'
      }
    }


@pytest.fixture
def metadata_response_sb():
    return {
      'og': {
        'url': 'https://www.scandiborn.co.uk/products/plum-play-discovery-woodland-treehouse',
        'site_name': 'Scandibørn',
        'type': 'product',
        'title': 'Plum Play Discovery Woodland Treehouse',
        'image': [
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-320911_grande.jpg?v=1584688457',
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-137566_grande.jpg?v=1584688457',
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-179087_grande.jpg?v=1584688457'
        ],
        'image:secure_url': [
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-320911_grande.jpg?v=1584688457',
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-137566_grande.jpg?v=1584688457',
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-179087_grande.jpg?v=1584688457'
        ],
        'price:amount': '399.95',
        'price:currency': 'GBP',
        'description': 'The Plum Play Discovery Woodland Treehouse is perfect for natures little ambassadors. Combining play, learning, creativity all year round, children can get up close with nature discovering all the wildlife hiding in the garden, practice their painting skills on the wipeable painting screen.'
      },
      'meta': {
        'description': 'The Plum Play Discovery Woodland Treehouse is perfect for natures little ambassadors. Combining play, learning, creativity all year round, children can get up close with nature discovering all the wildlife hiding in the garden, practice their painting skills on the wipeable painting screen.',
        'author': 'Scandibørn',
        'og:url': 'https://www.scandiborn.co.uk/products/plum-play-discovery-woodland-treehouse',
        'og:site_name': 'Scandibørn',
        'og:type': 'product',
        'og:title': 'Plum Play Discovery Woodland Treehouse',
        'og:image': [
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-320911_grande.jpg?v=1584688457',
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-137566_grande.jpg?v=1584688457',
          'http://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-179087_grande.jpg?v=1584688457'
        ],
        'og:image:secure_url': [
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-320911_grande.jpg?v=1584688457',
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-137566_grande.jpg?v=1584688457',
          'https://cdn.shopify.com/s/files/1/1257/2223/products/plum-play-discovery-woodland-treehouse-179087_grande.jpg?v=1584688457'
        ],
        'og:price:amount': '399.95',
        'og:price:currency': 'GBP',
        'og:description': 'The Plum Play Discovery Woodland Treehouse is perfect for natures little ambassadors. Combining play, learning, creativity all year round, children can get up close with nature discovering all the wildlife hiding in the garden, practice their painting skills on the wipeable painting screen.',
      },
      'dc': {},
      'page': {
        'title': 'Plum Play Discovery Woodland Treehouse | Scandiborn',
        'canonical': 'https://www.scandiborn.co.uk/products/plum-play-discovery-woodland-treehouse'
      }
    }


@pytest.fixture
def metadata_response_mp():
    return {
      'og': {
        'url': 'https://www.mamasandpapas.com/en-gb/santa-christmas-jumper/p/s22lxy2',
        'site_name': 'Mamas & Papas',
        'title': 'Santa Christmas Jumper',
        'type': 'product',
        'description': 'Get ready for cosy Christmas cuddles. Our Christmas 2020 range is filled with festive fun for your little one, with cute winter characters and merry prints.',
        'image': 'https://media.mamasandpapas.com/i/mamasandpapas/S22LXY2_HERO_SANTA XMAS JUMPER'
      },
      'meta': {
        'og:url': 'https://www.mamasandpapas.com/en-gb/santa-christmas-jumper/p/s22lxy2',
        'og:site_name': 'Mamas & Papas',
        'og:title': 'Santa Christmas Jumper',
        'og:type': 'product',
        'og:description': 'Get ready for cosy Christmas cuddles. Our Christmas 2020 range is filled with festive fun for your little one, with cute winter characters and merry prints.',
        'og:image': 'https://media.mamasandpapas.com/i/mamasandpapas/S22LXY2_HERO_SANTA XMAS JUMPER',
        'product:price:amount': '14.25',
        'product:price:currency': 'GBP'
      },
      'dc': {},
      'page': {
        'title': 'Santa Christmas Jumper | Mamas & Papas',
        'canonical': 'https://www.mamasandpapas.com/en-gb/santa-christmas-jumper/p/s22lxy2'
      }
    }


@pytest.fixture
def metadata_response_k():
    return {
      'og': {},
      'meta': {
        'og:site_name': 'KIDLY',
        'description': 'The KIDLY Label Recycled Gilet - A go-to warm layer with cool eco creds, to wear under rainwear or over hoodies, in colours to love.',
        'og:title': 'Buy the KIDLY Label Recycled Gilet at KIDLY UK',
        'og:url': '/products/kidly/recycled-gilet/9993',
        'og:type': 'product',
        'og:description': 'The KIDLY Label Recycled Gilet - A go-to warm layer with cool eco creds, to wear under rainwear or over hoodies, in colours to love.',
        'og:image': 'https://kidlycatalogue.blob.core.windows.net/products/9993/product-images/brown-toffee-1/kidly-puffa-gilet-brown-toffee-500x500_02.jpg',
        'og:image:type': 'image/jpeg',
        'og:image:width': '500',
        'og:image:height': '500'
      },
      'dc': {},
      'page': {
        'title': 'Buy the KIDLY Label Recycled Gilet at KIDLY UK',
        'canonical': 'https://www.kidly.co.uk/products/kidly/recycled-gilet/9993'
      }
    }
