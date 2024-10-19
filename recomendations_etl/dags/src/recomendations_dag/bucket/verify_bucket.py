import sys
import os
from dotenv import load_dotenv  # Importar load_dotenv

load_dotenv()

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..

from helpers.bucket.index import bucket_exists  # Asegúrate de que la ruta sea correcta
from helpers.bucket.index import create_bucket


def verify_bucket(bucket_name):
    if bucket_exists(bucket_name):
        print(f"El bucket '{bucket_name}' ya existe.")
    else:
        create_bucket(bucket_name)
        print(f"El bucket '{bucket_name}' ha sido creado.")