import os
import json
from jose import jwt, JWTError
from secretManager import getSecret

# Preload the secret key during cold start
try:
    # Load the secret once and store it for subsequent invocations
    secret_key = json.loads(getSecret(region=os.environ['AWS_REGION'], secret_manager_arn=os.environ['SECRET_ID']))['secretKey']
except Exception as e:
    # Handle any errors that occur during the loading of the secret
    secret_key = None
    error_loading_secret = f"Error loading secret: {e}"
else:
    error_loading_secret = None

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
    # Default principal ID if no valid token is found
    principal_id = '0000'
    
    # Check if there was an error loading the secret key
    if error_loading_secret:
        print(error_loading_secret)
        return generate_policy(principal_id, 'Deny', event['methodArn'], error_loading_secret)
    
    # Extract the JWT token from the event
    token = event.get('authorizationToken')
    if not token:
        error_message = "Missing authorization token."
        print(error_message)
        return generate_policy(principal_id, 'Deny', event['methodArn'], error_message)

    try:
        # Validate the JWT using the preloaded secret key
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        # If validation is successful, set the principal ID and allow access
        principal_id = payload.get('sub', principal_id)
        effect = 'Allow'
        error_message = None
    except JWTError as e:
        # Handle JWT errors and deny access
        error_message = f"Error validating JWT: {e}"
        print(error_message)
        effect = 'Deny'
    except Exception as e:
        # Handle any other exceptions and deny access
        error_message = f"Error: {e}"
        print(error_message)
        effect = 'Deny'

    # Generate and return the policy based on the result
    return generate_policy(principal_id, effect, event['methodArn'], error_message)
