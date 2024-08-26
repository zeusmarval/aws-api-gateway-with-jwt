import json

def lambda_handler(event, context):
    print(json.dumps(event))
    
    # Parse the incoming request body once
    data = json.loads(event['body'])
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Test Lambda c:',
            'data': json.dumps(data)
        })
    }
