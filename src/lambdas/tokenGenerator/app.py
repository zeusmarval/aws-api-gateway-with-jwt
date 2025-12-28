import os
import json
from jose import jwt
from datetime import datetime, timedelta
from common_libs.logger import logger
from common_libs.secretManager import get_secret

# Cache environment variables and pre-compute values during cold start
REGION = os.environ.get('AWS_REGION', 'us-east-1')
SECRET_ARN = os.environ.get('SECRET_ID')
EXPIRATION_DAYS = int(os.environ.get('DAYS', '7'))
expiration_duration = timedelta(days=EXPIRATION_DAYS)

def lambda_handler(event, context):
    start_time = datetime.utcnow()
    
    logger.info("Token generation request received", {
        "requestId": context.aws_request_id if context else None
    })
    
    # Validate configuration
    if not SECRET_ARN:
        logger.error("SECRET_ID environment variable is not configured", None, {
            "region": REGION
        })
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        return {
            'statusCode': 503,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': False,
                'message': 'Service unavailable',
                'error': 'Internal configuration error'
            })
        }
    
    try:
        # Get secret with caching (TTL configured via SECRET_CACHE_TTL_SECONDS env var)
        secret_data = get_secret(region=REGION, secret_manager_arn=SECRET_ARN)
        secret_key_value = json.loads(secret_data)['secretKey']
        # Parse the incoming request body
        if not event.get('body'):
            logger.warn("Missing request body")
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'success': False,
                    'message': 'Bad Request',
                    'error': 'Request body is required'
                })
            }
        
        data = json.loads(event['body'])
        
        # Validate the presence of 'username'
        username = data.get('username')
        if not username:
            logger.warn("Username not provided in request")
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'success': False,
                    'message': 'Bad Request',
                    'error': 'Username is required'
                })
            }

        # Get current time and compute expiration time
        current_time = datetime.utcnow()
        expiration_time = current_time + expiration_duration

        # Prepare the JWT payload
        payload = {
            'sub': str(int(current_time.timestamp())),
            'username': username,
            'exp': int(expiration_time.timestamp())
        }
        
        # Encode the JWT token with HS256 algorithm
        token = jwt.encode(payload, secret_key_value, algorithm='HS256')
        
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        logger.info("Token generated successfully", {
            "username": username,
            "expiration": expiration_time.isoformat() + "Z",
            "durationMs": duration_ms
        })
        
        # Return the response with the token and formatted expiration time
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'token': token,
                'expiration': expiration_time.isoformat() + "Z"
            })
        }
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in request body", e)
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': False,
                'message': 'Bad Request',
                'error': 'Invalid JSON format in request body'
            })
        }
    except Exception as e:
        logger.error("Error generating token", e, {
            "requestId": context.aws_request_id if context else None
        })
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': False,
                'message': 'Internal Server Error',
                'error': 'An unexpected error occurred'
            })
        }
