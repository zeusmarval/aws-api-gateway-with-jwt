import os
import json
from jose import jwt
from datetime import datetime, timedelta
from secretManager import getSecret

# Cache environment variables and pre-compute values during cold start
REGION = os.environ['AWS_REGION']
SECRET_ARN = os.environ['SECRET_ID']
EXPIRATION_DAYS = int(os.environ['DAYS'])

# Load only the needed secret value during cold start
secret_key_value = json.loads(getSecret(region=REGION, secret_manager_arn=SECRET_ARN))['secretkey']
expiration_duration = timedelta(days=EXPIRATION_DAYS)

def lambda_handler(event, context):
    try:
        # Parse the incoming request body once
        data = json.loads(event['body'])
        
        # Validate the presence of 'username'
        username = data.get('username')
        if not username:
            return {
                'statusCode': 400,
                'body': 'Username is required'  # No JSON encoding for static error messages
            }

        # Get current time and compute expiration time
        current_time = datetime.utcnow()
        expiration_time = current_time + expiration_duration

        # Prepare the JWT payload
        payload = {
            'sub': str(int(current_time.timestamp())),  # Direct timestamp conversion
            'username': username,
            'exp': int(expiration_time.timestamp())
        }
        
        # Encode the JWT token with HS256 algorithm
        token = jwt.encode(payload, secret_key_value, algorithm='HS256')
        
        # Return the response with the token and formatted expiration time
        return {
            'statusCode': 200,
            'body': json.dumps({
                'token': token,
                'expiration': expiration_time.isoformat()  # Use isoformat for consistent time formatting
            })
        }
    except Exception as e:
        # Log the error and return a generic message
        print(f'Error: {str(e)}')
        return {
            'statusCode': 500,
            'body': 'Internal server error'  # Keep the error message simple and avoid JSON conversion
        }
