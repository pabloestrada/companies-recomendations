import boto3
import os
from dotenv import load_dotenv 
from botocore.exceptions import ClientError  # Asegúrate de importar ClientError

load_dotenv()

# Obtener las variables de entorno o usar valores predeterminados para Localstack
endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "test")  # Credenciales ficticias para Localstack
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "test")  # Credenciales ficticias
aws_region = os.getenv("AWS_REGION", "us-east-1")  # Región predeterminada

# Crear el cliente S3 con las credenciales obtenidas desde variables de entorno
s3 = boto3.client(
    's3',
    endpoint_url=endpoint_url,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

def bucket_exists(bucket_name):
    try:
        s3.head_bucket(Bucket=bucket_name)  # Verificar si el bucket existe
        return True
    except ClientError:
        return False
    
def create_bucket(bucket_name):
    s3.create_bucket(Bucket=bucket_name)
    print(f"Bucket creado: {bucket_name}")

def put_file_s3(bucket_name, file_name, data):

    s3.put_object(Bucket=bucket_name, Key=file_name, Body=data)
    
    print(f"Resultados guardados en S3: s3://{bucket_name}/{file_name}")
    return f"s3://{bucket_name}/{file_name}" 

def get_file_s3(bucket_name, file_name):
    print(f"bucket_name: {bucket_name}")
    print(f"file_name: {file_name}")
    try:
        # Obtener el objeto del bucket
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        
        # Leer el archivo en un buffer binario
        file_content = response['Body'].read()

        return file_content  # Devolver el archivo tal cual, en formato binario
    except Exception as e:
        print(f"Error al obtener el archivo: {e}")
        return None