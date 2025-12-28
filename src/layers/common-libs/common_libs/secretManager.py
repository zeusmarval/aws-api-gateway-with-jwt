import os
import time
import base64
import boto3
from typing import Optional
from botocore.exceptions import ClientError
from common_libs.logger import logger

# Cache for secrets with TTL
_cached_secrets: dict[str, dict] = {}
_cache_timestamp: dict[str, float] = {}

# Default TTL in seconds (15 minutes)
DEFAULT_SECRET_TTL = int(os.environ.get("SECRET_CACHE_TTL_SECONDS", "900"))


def get_secret(
    region: str,
    secret_manager_arn: str,
    ttl_seconds: Optional[int] = None
) -> str:
    """
    Retrieves a secret from AWS Secrets Manager with caching and TTL support.
    
    Args:
        region: AWS region where the secret is stored
        secret_manager_arn: ARN or name of the secret in Secrets Manager
        ttl_seconds: Time to live for the cache in seconds (defaults to SECRET_CACHE_TTL_SECONDS env var or 900)
    
    Returns:
        The secret value as a string
    
    Raises:
        ClientError: If there's an error retrieving the secret from AWS
        Exception: For other unexpected errors
    """
    cache_key = f"{region}:{secret_manager_arn}"
    ttl = ttl_seconds if ttl_seconds is not None else DEFAULT_SECRET_TTL
    current_time = time.time()
    
    # Check if secret is cached and still valid
    if cache_key in _cached_secrets:
        cache_age = current_time - _cache_timestamp.get(cache_key, 0)
        if cache_age < ttl:
            logger.info("Secret retrieved from cache", {
                "region": region,
                "secretArn": secret_manager_arn,
                "cacheAge": int(cache_age)
            })
            return _cached_secrets[cache_key]["value"]
        else:
            # Cache expired, remove it
            logger.info("Secret cache expired, refreshing", {
                "region": region,
                "secretArn": secret_manager_arn,
                "cacheAge": int(cache_age),
                "ttl": ttl
            })
            del _cached_secrets[cache_key]
            del _cache_timestamp[cache_key]
    
    # Secret not in cache or expired, fetch from AWS
    service_name = "secretsmanager"
    secret_string_key = "SecretString"
    secret_binary_key = "SecretBinary"
    text_encode_key = "utf-8"
    
    session = boto3.session.Session()
    client = session.client(region_name=region, service_name=service_name)
    
    try:
        secret_value: dict = client.get_secret_value(SecretId=secret_manager_arn)
        
        if secret_string_key in secret_value:
            secret_data = secret_value[secret_string_key]
        else:
            secret_binary: bytes = base64.b64decode(secret_value[secret_binary_key])
            secret_data = secret_binary.decode(text_encode_key)
        
        # Cache the secret
        _cached_secrets[cache_key] = {"value": secret_data}
        _cache_timestamp[cache_key] = current_time
        
        logger.info("Secret retrieved from AWS Secrets Manager and cached", {
            "region": region,
            "secretArn": secret_manager_arn,
            "ttl": ttl
        })
        
        return secret_data
        
    except ClientError as err:
        error_code = err.response.get("Error", {}).get("Code", "Unknown")
        
        if error_code == "ResourceNotFoundException":
            error_msg = f"The requested secret {secret_manager_arn} was not found"
            logger.error("Secret not found in AWS Secrets Manager", err, {
                "region": region,
                "secretArn": secret_manager_arn,
                "errorCode": error_code
            })
        else:
            error_msg = f"An error occurred retrieving the secret: {error_code}"
            logger.error("Error retrieving secret from AWS Secrets Manager", err, {
                "region": region,
                "secretArn": secret_manager_arn,
                "errorCode": error_code
            })
        
        raise err
        
    except Exception as err:
        logger.error("Unexpected error retrieving secret", err, {
            "region": region,
            "secretArn": secret_manager_arn
        })
        raise err

