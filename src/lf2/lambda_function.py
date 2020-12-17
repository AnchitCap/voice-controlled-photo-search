import json
import boto3
from requests_aws4auth import AWS4Auth
import requests
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

esHost = 'https://search-photos-djn4fxsaja5jn5ycdo5mg76k7e.us-east-1.es.amazonaws.com'
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

def search_photo(keyword):
    body = {
        "size" : 1000,
        "query": {
            "match":{"labels" : keyword.lower()}
        }
    }
    search_data_url = esHost + "/photos/_search"
    r = requests.get(search_data_url, auth=awsauth, json=body)
    logger.info(r.text)
    return r.text
    
def lambda_handler(event, context):
    """
    #========== Test Search Image ============
    label = 'Person'
    search_photo(label)
    """
    
    # logger.info(event)
    body = {}
    keywords = []
    lexClient = boto3.client('lex-runtime')
    # queryString = event['msg']
    # queryString = event['queryStringParameters']['msg']
    queryString = event["queryStringParameters"]['q']
    logger.info(queryString)
    response = lexClient.post_text(
        botName='PhotoSearchBot',
        botAlias='$LATEST',
        userId='test',
        inputText= queryString
    )
    #message = response['message']
    try:
        #temp_keywords = message.split(',')
        #for entry in temp_keywords:
            #keywords.append(entry.split(':')[1].strip())
        slots = response['slots']
        keywords.append(slots['FirstKeyword'])
        keywords.append(slots['SecondKeyword'])
        logger.info(keywords)
    except Exception as e:
        print(e)
        body = {'Responses':[]}
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
            },
            'body': json.dumps(body)
        }
    
    logger.info(keywords)
    body = {'Responses':[]}
    for item in keywords:
        if (item == None):
            continue
        res = search_photo(item)
        parsed_res = json.loads(res)

        numMatched = parsed_res["hits"]["total"]["value"]
        #if no results corresponding to the labels are found
        if numMatched == 0:
            continue
        else:
            # body = {'Responses':[]}
            for i in range(numMatched):
                current_labels = parsed_res["hits"]["hits"][i]["_source"]["labels"]
                
                current_key = parsed_res["hits"]["hits"][i]["_source"]["objectKey"]
                current_url = "https://a3-b2-jars.s3.amazonaws.com/" + current_key

                response = {'url': current_url}
                body['Responses'].append(response)
                
    return {
        'statusCode': 200,
        'headers': {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        'body': json.dumps(body)
    }