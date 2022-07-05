import json
import requests
import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event,context):
    endpoint = 'https://search-posts-d3rxisx3z4py7255r4y6jmncl4.us-east-1.es.amazonaws.com'
    headers = { "Content-Type": "application/json" }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('posts')
    responses = []
    
    index = "posts"
    query = {
        "query": {
            "match": {
                "tags": event["q"]
            }
        },
         "size": 3   
    }
    url = endpoint + '/' + index + '/_search'
    result = json.loads(requests.get(url, auth=('randygenere', 'zokbim-niBbik-danso0'),headers=headers, data=json.dumps(query)).text)
    
    if(len(result['hits']['hits']) == 0):
        responses.append('no answers found for this category')
        return {
            'statusCode': 200,
            'body': json.dumps(responses)
        } 
    else:
        for hit in result['hits']['hits']:
            item = table.query(KeyConditionExpression=Key('id').eq(int(hit['_id'])))
            responses.append(item['Items'][0]['posts'])
            
        return {
            'statusCode': 200,
            'body': json.dumps(responses)
        } 
        