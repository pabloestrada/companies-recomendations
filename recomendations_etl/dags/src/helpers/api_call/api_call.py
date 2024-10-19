import os
from dotenv import load_dotenv  # Importar load_dotenv
import requests

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def api_call(path, params):
    url = os.getenv("API_URL")  # URL base
    endpoint = f"/{path}"  # Usar el path proporcionado
    response = requests.get(url + endpoint, params=params)  # Pasar los parámetros de búsqueda
    if response.status_code == 200:
        return response.json()  # Retornar los datos en formato JSON
    else:
        print(f"Error al consultar la API: {response.status_code}")  # Imprimir el error
        return None  # Retornar None en caso de error
