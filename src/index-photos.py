import os
import json
import boto3
import logging
import requests
from requests_aws4auth import AWS4Auth
from boto3.dynamodb.conditions import Key, Attr

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

esHost = 'https://search-photos-djn4fxsaja5jn5ycdo5mg76k7e.us-east-1.es.amazonaws.com'
region = 'us-east-1'
service = 'es'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

def detect_labels(bucket_name, key):
    rekognition_client = boto3.client('rekognition')
    response = rekognition_client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': key,
            },
        }
    )
    labels = []
    for l in response['Labels']:
        labels.append(l['Name'])
    return labels

def build_index():
    create_index_url = esHost + "/photos"
    body = {
        "mappings" : {
            "properties": {
                "objectKey" : {
                    "type" : "keyword"
                },
                "bucket" : {
                    "type" : "text"
                },
                "createdTimestamp" : {
                    "type" : "text"
                },
                "labels" : {
                    "type" : "object"
                }
            }
        }
    }
    r = requests.put(create_index_url, auth=awsauth, json=body)
    logger.info(r.text)

def delete_index():
    delete_index_url = esHost + "/photos"
    r = requests.delete(delete_index_url, auth=awsauth)
    print(r.text)

def create_index(bucket_name, key, labels, createdTimestamp):
    index_url = esHost + "/photos/_doc"
    body = {
        "objectKey" : key,
        "bucket": bucket_name,
        "createdTimestamp": createdTimestamp,
        "labels": labels
    }
    r = requests.post(index_url, auth=awsauth, json=body)
    logger.info(r.text)
    

def lambda_handler(event, context):
    logger.info(event['Records'])
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    createdTimestamp = event['Records'][0]['eventTime']
    
    logger.info("key is " + str(key))
    logger.info("bucket name is " + str(bucket_name))
    
    labels = detect_labels(bucket_name, key)
    logger.info("label is " + str(labels))
    
    create_index(bucket_name, key, labels, createdTimestamp)
    
    # ========= TEST CODE ==========
    # test_labels = ["person", "dog"]
    # build_index()
    # delete_index()
    # create_index(bucket_name, key, test_labels, createdTimestamp)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }