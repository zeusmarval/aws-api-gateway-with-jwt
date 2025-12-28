import json
from datetime import datetime
from common_libs.logger import logger

def lambda_handler(event, context):
    start_time = datetime.utcnow()
    
    logger.info("Test Lambda request received", {
        "requestId": context.aws_request_id if context else None,
        "httpMethod": event.get("httpMethod"),
        "path": event.get("path")
    })
    
    try:
        # Parse the incoming request body
        body = event.get('body')
        if not body:
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
        
        data = json.loads(body)
        
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        logger.info("Test Lambda processed successfully", {
            "durationMs": duration_ms
        })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Test Lambda executed successfully',
                'data': data,
                'durationMs': duration_ms
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
        logger.error("Error processing test request", e, {
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
