import boto3
import json
from datetime import datetime

new_id = 432009

def lambda_handler(event, context):
    global new_id
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('posts')
    
    try:
        now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        table.put_item(
            Item={
                'id': new_id,
                'date': now,
                'posts': event['post']
            }
        )
        
    except Exception as e:
        return {
            'statusCode': 200,
            'body': json.dumps(str(e))
        }
    
    else:
        new_id = new_id + 1
        return {
            'statusCode': 200,
            'body': json.dumps('Succesfully uploaded post')
        }
