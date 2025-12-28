import os
import json
from jose import jwt, JWTError
from common_libs.logger import logger
from common_libs.secretManager import get_secret
from datetime import datetime

# Cache environment variables during cold start
REGION = os.environ.get('AWS_REGION', 'us-east-1')
SECRET_ARN = os.environ.get('SECRET_ID')

# Predefine the basic policy structure function
def generate_policy(principal_id, effect, method_arn, error_message=None):
    # Create the basic policy document with the given parameters
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': method_arn
                }
            ]
        }
    }

    # Include an error message in the context if provided
    if error_message:
        policy['context'] = {
            'errorMessage': error_message
        }
    
    return policy

def lambda_handler(event, context):
    start_time = datetime.utcnow()
    
    # Default principal ID if no valid token is found
    principal_id = '0000'
    method_arn = event.get('methodArn', '')
    
    logger.info("JWT authorization request received", {
        "methodArn": method_arn
    })
    
    # Validate configuration
    if not SECRET_ARN:
        logger.error("SECRET_ID environment variable is not configured", None, {
            "region": REGION
        })
        return generate_policy(principal_id, 'Deny', method_arn, 'Internal configuration error')
    
    # Extract the JWT token from the event
    token = event.get('authorizationToken')
    if not token:
        error_message = "Missing authorization token"
        logger.warn("Authorization token missing", {
            "methodArn": method_arn
        })
        return generate_policy(principal_id, 'Deny', method_arn, error_message)

    try:
        # Get secret with caching (TTL configured via SECRET_CACHE_TTL_SECONDS env var)
        secret_data = get_secret(region=REGION, secret_manager_arn=SECRET_ARN)
        secret_key = json.loads(secret_data)['secretKey']
        
        # Validate the JWT using the secret key
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        # If validation is successful, set the principal ID and allow access
        principal_id = payload.get('sub', principal_id)
        username = payload.get('username', 'unknown')
        effect = 'Allow'
        error_message = None
        
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        logger.info("JWT token validated successfully", {
            "principalId": principal_id,
            "username": username,
            "effect": effect,
            "durationMs": duration_ms
        })
        
    except JWTError as e:
        # Handle JWT errors and deny access
        error_message = f"Invalid or expired JWT token"
        logger.warn("JWT validation failed", {
            "error": str(e),
            "methodArn": method_arn
        })
        effect = 'Deny'
    except Exception as e:
        # Handle any other exceptions and deny access
        error_message = f"Error processing authorization request"
        logger.error("Unexpected error during JWT validation", e, {
            "methodArn": method_arn
        })
        effect = 'Deny'

    # Generate and return the policy based on the result
    return generate_policy(principal_id, effect, method_arn, error_message)
