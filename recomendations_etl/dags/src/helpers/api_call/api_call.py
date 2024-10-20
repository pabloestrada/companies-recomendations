import os
from dotenv import load_dotenv  # Importar load_dotenv
import requests

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def api_call(path, params):
    url = os.getenv("API_URL")  # URL base
    endpoint = f"/{path}"  # Usar el path proporcionado
    try:
        response = requests.get(url + endpoint, params=params)  # Pasar los parámetros de búsqueda
        response.raise_for_status()  # Raise an error for bad status codes (4xx/5xx)
        return response.json()  # Retornar los datos en formato JSON
    except requests.exceptions.RequestException as e:
        print(f"Error al consultar la API: {response.status_code}, {e}")  # Imprimir el error
        raise e  # Raise the caught exception # Retornar None en caso de error
    
    
def api_call_training(params):
    url = os.getenv("API_URL_TRAINING")  # URL base

    try:
        # Realizar la solicitud POST con el cuerpo en formato JSON
        response = requests.post(url, json=params)  # Usar json para parámetros en el cuerpo
        response.raise_for_status()  # Lanza una excepción para códigos de estado HTTP 4xx/5xx

        # Si la solicitud fue exitosa, devolver el JSON
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al consultar la API: {e}")
        raise  # Retornar None en caso de error
