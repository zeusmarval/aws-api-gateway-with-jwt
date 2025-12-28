# API Gateway with JWT Authentication

This repository contains a serverless application built with AWS SAM that implements a REST API using API Gateway with JWT authentication via AWS Lambda.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Deployment](#deployment)
- [Usage](#usage)
  - [Generate JWT Token](#generate-jwt-token)
  - [Use Protected Endpoints](#use-protected-endpoints)
  - [Test Endpoint](#test-endpoint)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Secrets Management](#secrets-management)
- [Lambda Functions](#lambda-functions)
  - [JWT Authorizer](#jwt-authorizer)
  - [Token Generator](#token-generator)
  - [Lambda Test](#lambda-test)
- [Common Layer](#common-layer)
- [Clean Up](#clean-up)
- [References](#references)

## Overview

This serverless application provides a complete solution for JWT authentication in API Gateway. The SAM template creates the following AWS resources:

- **AWS Lambda Functions**: Functions for JWT authentication, token generation, and test endpoint
- **AWS Secrets Manager**: Securely stores the JWT secret key
- **API Gateway REST API**: Provides REST endpoints protected with Lambda Authorizer
- **AWS Lambda Layer**: Common layer with shared utilities (logger and secretManager)
- **CloudWatch Log Groups**: Log groups with configurable retention per environment

## Features

- **JWT Authentication**: Uses a Lambda Authorizer to validate JWT tokens in API Gateway
- **Token Generation**: Dedicated endpoint to generate JWT tokens without authentication
- **Secure Configuration**: JWT secret key is stored securely in AWS Secrets Manager
- **Secret Caching**: Implements caching with TTL to reduce latency and costs
- **Structured Logging**: Structured logging system with sensitive data sanitization
- **CORS Configured**: CORS support for all endpoints
- **Multiple Environments**: Support for dev, qa, and prod environments via parameters

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│      API Gateway REST API           │
│  ┌───────────────────────────────┐  │
│  │  POST /token (No Auth)        │  │
│  └───────────┬───────────────────┘  │
│  ┌───────────▼───────────────────┐  │
│  │  POST /test (JWT Auth)        │  │
│  └───────────┬───────────────────┘  │
└──────────────┼───────────────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
┌─────────────┐  ┌──────────────────┐
│   Lambda    │  │  Lambda           │
│  Authorizer │  │  Token Generator  │
└──────┬──────┘  └────────┬─────────┘
       │                  │
       │                  │
       ▼                  ▼
┌─────────────┐  ┌──────────────────┐
│  Secrets    │  │  Secrets          │
│  Manager    │  │  Manager          │
└─────────────┘  └──────────────────┘
```

## Prerequisites

- An AWS account
- AWS CLI configured with appropriate permissions
- AWS SAM CLI installed
- Python 3.13 (Lambda functions runtime)
- Docker (optional, for builds with `--use-container`)

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/zeusmarval/aws-api-gateway-with-jwt.git
cd aws-api-gateway-with-jwt
```

2. **Install Lambda function dependencies:**

Dependencies are automatically installed during SAM build. Lambda functions use the following dependencies:

- `python-jose==3.3.0` (for JWT)
- `boto3` (included in Lambda runtime)

## Deployment

### Option 1: Using AWS SAM CLI (Recommended)

1. **Build the application:**

```bash
sam build --use-container
```

2. **Deploy the stack:**

```bash
sam deploy
```

The `sam deploy` command uses the configuration in `samconfig.toml`. To deploy to a different environment, you can modify the file or use parameters:

```bash
sam deploy --parameter-overrides Environment=qa
```

### Option 2: Using AWS CloudFormation directly

```bash
sam build --use-container
sam package --output-template-file packaged.yaml --s3-bucket YOUR_S3_BUCKET
aws cloudformation deploy \
    --template-file packaged.yaml \
    --stack-name dev-api-jwt \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides Environment=dev
```

### Stack Parameters

- **Environment**: Deployment environment (dev, qa, prod). Default: `dev`

## Usage

### Generate JWT Token

To obtain a JWT token, make a POST request to the `/token` endpoint:

```bash
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/v1/token \
  -H "Content-Type: application/json" \
  -d '{"username": "user123"}'
```

**Successful response:**

```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiration": "2024-01-15T12:00:00Z"
}
```

**Parameters:**
- `username` (required): Username to include in the token

**Note:** This endpoint does not require authentication.

### Use Protected Endpoints

To access protected endpoints, include the JWT token in the `Authorization` header:

```bash
curl -X POST https://YOUR_API_ID.execute-api.us-east-1.amazonaws.com/v1/test \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -d '{"data": "test"}'
```

**Successful response:**

```json
{
  "success": true,
  "message": "Test Lambda executed successfully",
  "data": {"data": "test"},
  "durationMs": 15
}
```

### Test Endpoint

The `/test` endpoint is available to validate that JWT authentication works correctly:

- **Path**: `/test`
- **Method**: `POST`
- **Authentication**: Required (JWT)
- **Body**: JSON with any data

## Project Structure

```
aws-api-gateway-with-jwt/
├── src/
│   ├── lambdas/
│   │   ├── jwtAuthorizer/        # Lambda Authorizer to validate JWT
│   │   │   ├── app.py
│   │   │   └── requirements.txt
│   │   ├── tokenGenerator/       # Lambda to generate JWT tokens
│   │   │   ├── app.py
│   │   │   └── requirements.txt
│   │   └── lambdaTest/           # Test Lambda for protected endpoints
│   │       └── app.py
│   └── layers/
│       └── common-libs/          # Common layer with shared utilities
│           ├── common_libs/
│           │   ├── __init__.py
│           │   ├── logger.py     # Structured logging system
│           │   └── secretManager.py  # Secrets management with caching
│           └── requirements.txt
├── events/                        # Test events for local testing
│   └── bodyEndpoint.json
├── template.yml                   # SAM/CloudFormation template
├── samconfig.toml                 # SAM CLI configuration
└── README.md
```

## Configuration

### Environment Variables

Lambda functions use the following environment variables:

#### JWT Authorizer Function
- `SECRET_ID`: ARN or name of the secret in Secrets Manager (automatically configured)
- `SECRET_CACHE_TTL_SECONDS`: Secret cache TTL in seconds (default: 900)

#### Token Generator Function
- `SECRET_ID`: ARN or name of the secret in Secrets Manager (automatically configured)
- `DAYS`: JWT token expiration days (default: 7)
- `SECRET_CACHE_TTL_SECONDS`: Secret cache TTL in seconds (default: 900)

### Secrets Management

The JWT secret is automatically created during deployment in AWS Secrets Manager:

- **Name**: `{stack-name}-jwt-secret`
- **Format**: JSON with the `secretKey` key
- **Generation**: Automatically generates a 32-character key

**Example secret structure:**

```json
{
  "secretKey": "abc123def456ghi789jkl012mno345pq"
}
```

## Lambda Functions

### JWT Authorizer

**Description**: Validates JWT tokens to authorize requests to API Gateway.

- **Handler**: `app.lambda_handler`
- **Runtime**: Python 3.13
- **Timeout**: 25 seconds
- **Layer**: Uses `CommonLibsLayer` for logger and secretManager

**Authorization flow:**
1. Extracts token from `Authorization` header
2. Retrieves secret key from Secrets Manager (with caching)
3. Validates JWT token using HS256 algorithm
4. Returns an IAM policy `Allow` or `Deny`

### Token Generator

**Description**: Generates JWT tokens for authentication.

- **Handler**: `app.lambda_handler`
- **Runtime**: Python 3.13
- **Timeout**: 25 seconds
- **Endpoint**: `POST /token` (no authentication required)
- **Layer**: Uses `CommonLibsLayer` for logger and secretManager

**JWT token payload:**
- `sub`: Creation timestamp
- `username`: Provided username
- `exp`: Expiration timestamp (configurable via `DAYS` environment variable)

### Lambda Test

**Description**: Test endpoint to validate that JWT authentication works correctly.

- **Handler**: `app.lambda_handler`
- **Runtime**: Python 3.13
- **Timeout**: 25 seconds
- **Endpoint**: `POST /test` (requires JWT authentication)
- **Layer**: Uses `CommonLibsLayer` for logger

## Common Layer

The `CommonLibsLayer` contains shared utilities used by all Lambda functions:

### Logger (`common_libs/logger.py`)

Structured logging system with:
- JSON formatted logs
- Automatic sanitization of sensitive data (tokens, secrets, passwords)
- Levels: INFO, WARN, ERROR
- Timestamps in ISO 8601 UTC format

**Usage example:**

```python
from common_libs.logger import logger

logger.info("Informative message", {"key": "value"})
logger.error("Error occurred", exception, {"context": "data"})
logger.warn("Warning", {"warning": "info"})
```

### Secret Manager (`common_libs/secretManager.py`)

Secrets management with TTL caching:
- In-memory cache with configurable TTL
- Reduces calls to Secrets Manager
- Support for String and Binary format secrets
- Robust error handling

**Usage example:**

```python
from common_libs.secretManager import get_secret

secret_data = get_secret(
    region="us-east-1",
    secret_manager_arn="arn:aws:secretsmanager:...",
    ttl_seconds=900  # Optional
)
```

## Clean Up

To delete the CloudFormation stack and all created resources:

```bash
aws cloudformation delete-stack --stack-name dev-api-jwt
```

**Note**: The secret in Secrets Manager has `UpdateReplacePolicy: Retain`, so it will not be automatically deleted. If you want to delete it manually:

```bash
aws secretsmanager delete-secret \
  --secret-id dev-api-jwt-jwt-secret \
  --force-delete-without-recovery
```

## References

- [AWS Lambda Authorizer in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- [Introduction to JWT](https://jwt.io/introduction/)
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)
- [python-jose Library](https://python-jose.readthedocs.io/)
