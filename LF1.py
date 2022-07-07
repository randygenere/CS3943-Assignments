import json
import requests
import boto3
from boto3.dynamodb.conditions import Key, Attr

endpoint = 'https://search-posts-d3rxisx3z4py7255r4y6jmncl4.us-east-1.es.amazonaws.com'
headers = { "Content-Type": "application/json" }
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('posts')
sns = boto3.client('sns')

def lambda_handler(event,context):
    global endpoint, headers, dynamodb, table, sns
    
    keyword1 = event["currentIntent"]["slots"]["First_Keyword"]
    keyword2 = event["currentIntent"]["slots"]["Second_Keyword"]
    
    if keyword1 == None:
        response = {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "This is not a valid query please try again."
                }
            }
        }
    elif keyword2 == None:
        response = {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "Great! I will try to find posts relating to {}. Please check your email for a response.".format(keyword1)
                }
            }
        }
    else:
        response = {
            "dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "Great! I will try to find posts relating to {} and {}. Please check your email for a response.".format(keyword1, keyword2)
                }
            }
        }
    
    
    
    keyword1Posts = findPosts(keyword1)
    keyword2Posts = findPosts(keyword2)
    
    keyword1Responses = createResponseKeyword1(keyword1Posts, keyword1)
    keyword2Responses = []
    
    if (keyword2 != None): keyword2Responses = createResponseKeyword2(keyword2Posts, keyword2)
    
    sendResponse(keyword1Responses, keyword2Responses, keyword1, keyword2)
    
    return response
    
def findPosts(tag):
    index = "posts"
    query = {
        "query": {
            "match": {
                "tags": tag
            }
        },
         "size": 3   
    }
    
    url = endpoint + '/' + index + '/_search'
    result = json.loads(requests.get(url, auth=('randygenere', 'zokbim-niBbik-danso0'),headers=headers, data=json.dumps(query)).text)
    return result

def createResponseKeyword1(posts, keyword):
    keyword1Responses = []
    
    if(len(posts['hits']['hits']) > 0):
        for post in posts['hits']['hits']:
            item = table.query(KeyConditionExpression=Key('id').eq(int(post['_id'])))
            keyword1Responses.append(item['Items'][0]['posts'])
            
    return keyword1Responses
            
def createResponseKeyword2(posts, keyword):
    keyword2Responses = []
    
    if(len(posts['hits']['hits']) == 0):
        keyword2Responses.append("No posts found relating to {}.".format(keyword))
    else:
        for post in posts['hits']['hits']:
            item = table.query(KeyConditionExpression=Key('id').eq(int(post['_id'])))
            keyword2Responses.append(item['Items'][0]['posts'])
            
    return keyword2Responses
    
def sendResponse(keyword1Responses, keyword2Responses, keyword1, keyword2):
    if len(keyword1Responses) == 0 and len(keyword2Responses) == 0:
        sns.publish (
            TargetArn = "arn:aws:sns:us-east-1:773136982463:QueryResponse",
            Subject = "Response to Query",
            Message = json.dumps({'default': "Sorry. We were not able to find any posts relating to your query."}),
            MessageStructure = 'json'
        )
    elif len(keyword1Responses) > 0 and len(keyword2Responses) == 0:
        emailBody = "These are the posts we found relating to {}:".format(keyword1)
        for post in keyword1Responses:
            postNumber = keyword1Responses.index(post) + 1
            emailBody = emailBody + "\n\t" + str(postNumber) + ". " + post + "\n"
        
        sns.publish (
            TargetArn = "arn:aws:sns:us-east-1:773136982463:QueryResponse",
            Subject = "Response to Query",
            Message = json.dumps({'default': emailBody}),
            MessageStructure = 'json'
        )
    elif len(keyword1Responses) > 0 and len(keyword2Responses) > 0:
        emailBody = "These are the posts we found relating to {}:".format(keyword1)
        for post in keyword1Responses:
            postNumber = keyword1Responses.index(post) + 1
            emailBody = emailBody + "\n\t" + str(postNumber) + ". " + post + "\n"
            
        emailBody = emailBody + "\nThese are the posts we found relating to {}:".format(keyword2)  
        for post in keyword2Responses:
            postNumber = keyword2Responses.index(post) + 1
            emailBody = emailBody + "\n\t" + str(postNumber) + ". " + post + "\n"
        
        sns.publish (
            TargetArn = "arn:aws:sns:us-east-1:773136982463:QueryResponse",
            Subject = "Response to Query",
            Message = json.dumps({'default': emailBody}),
            MessageStructure = 'json'
        )
        
