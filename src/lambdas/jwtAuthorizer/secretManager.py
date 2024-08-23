

import base64
import boto3
from botocore.exceptions import ClientError

def getSecret(region:str, secret_manager_arn:str) -> str:
    
    _SERVICE_NAME : str = "secretsmanager"
    _SECRET_STRING_KEY : str = "SecretString"
    _SECRET_BINARY_KEY : str = "SecretBinary"
    _TEXT_ENCODE_KEY : str = "utf-8"

    session = boto3.session.Session()
    client = session.client( region_name=region,service_name=_SERVICE_NAME)
    
    try:
        
        secret_value : dict[str,any]= client.get_secret_value(SecretId=secret_manager_arn)
        if _SECRET_STRING_KEY in secret_value:
            return secret_value[_SECRET_STRING_KEY]
        else:
            secret_binary : bytes = base64.b64decode(secret_value[_SECRET_BINARY_KEY])
            return secret_binary.decode(_TEXT_ENCODE_KEY)
            
    except ClientError as err:
        
        if(err.response["Error"]["Code"] == "ResourceNotFoundException"):
            msg :str = f"The requested secret {secret_manager_arn} was not found."
            print(f'{str("{")}"msg":"{msg}","level":"ERROR"{str("}")}')
        else:
            print(f'{str("{")}"msg": "An unknown error occurred: {str(err)}","level":"ERROR"{str("}")}')
        raise err

    except Exception as err:
        print(f'{str("{")}"msg": "An unknown error occurred: {str(err)}" ,"level":"ERROR"{str("}")}')
        raise err

