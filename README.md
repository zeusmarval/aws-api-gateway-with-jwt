# API Gateway with JWT Authentication

This repository contains an AWS CloudFormation template to set up a serverless application using API Gateway with JWT authentication via AWS Lambda.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Deployment](#deployment)
- [Usage](#usage)
  - [JWT Authorizer](#jwt-authorizer)
  - [Token Generator Function](#token-generator-function)
  - [IAM Policies](#iam-policies)
  - [Secret Management](#secret-management)
- [Clean Up](#clean-up)
- [References](#references)

## Overview

The template provisions the following AWS resources:

- **AWS Lambda**: Functions to handle JWT authentication and token generation.
- **AWS Secrets Manager**: Securely stores the JWT secret key.
- **API Gateway**: Provides REST API endpoints secured with a Lambda Authorizer.

## Features

- **JWT Authentication**: Uses a Lambda Authorizer to validate JWT tokens for API Gateway.
- **Token Generation**: A dedicated Lambda function to generate JWT tokens.
- **Secure Configuration**: The JWT secret key is stored securely in AWS Secrets Manager.

## Prerequisites

- An AWS account.
- AWS CLI configured with appropriate permissions.
- Python 3.12 runtime environment.

## Deployment

1. **Clone the repository:**

    ```sh
    git clone https://github.com/zeusmarval/aws-api-gateway-with-jwt.git
    cd api-gateway-with-jwt
    ```

2. **Package the stack:**

    ```sh
    sam build --use-container
    ```

3. **Deploy the CloudFormation stack:**

    ```sh
    aws cloudformation deploy \
        --template-file template.yaml \
        --stack-name ApiGatewayWithJWT \
        --capabilities CAPABILITY_IAM
    ```

## Usage

### JWT Authorizer

- **Handler**: The entry point for the JWT authorizer function is defined in the `app.lambda_handler` file located in the `src/lambdas/jwtAuthorizer` directory.
- **Runtime**: Python 3.12 is used as the runtime environment.
- **Authorization**: The Lambda Authorizer checks JWT tokens for requests to secured API Gateway endpoints.

### Token Generator Function

- **Handler**: The entry point for the token generator function is defined in the `app.lambda_handler` file located in the `src/lambdas/tokenGenerator` directory.
- **Path**: The function is invoked at the `/token` endpoint via a POST request.
- **Authentication**: This endpoint does not require authentication, allowing clients to request a new JWT.

### IAM Policies

The Lambda functions have the following permissions:

- **Actions**:
  - `secretsmanager:GetSecretValue`
- **Resource**: Restricted to the specific Secrets Manager resource holding the JWT secret.

### Secret Management

- **AWS Secrets Manager**: Stores the JWT secret key securely with the following configuration:
  - `secretKey`: The secret key used for signing JWT tokens.

## Clean Up

To delete the CloudFormation stack and all resources created:

```sh
aws cloudformation delete-stack --stack-name ApiGatewayWithJWT
```

## References

- AWS Lambda Authorizer: [Lambda Authorizer in API Gateway](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-use-lambda-authorizer.html)
- JWT Authentication: [Introduction to JWT](https://jwt.io/introduction/)
- AWS Secrets Manager: [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
