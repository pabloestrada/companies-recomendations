import sys
import os
import io 
from dotenv import load_dotenv  # Importar load_dotenv
# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..

from helpers.api_call.api_call import api_call  # Asegúrate de que la ruta sea correcta

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..
from helpers.database.companies import insert_companies  # Asegúrate de que la ruta sea correcta

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def save_companies_to_db(limit=1000, offset=0):
    
    path = "companies"  # El path que deseas consultar
    params = {
        "limit": limit,  # Usar el valor de limit proporcionado
        "offset": offset  # Usar el valor de offset proporcionado
    }
    

    results = []  # Lista para almacenar todos los resultados
    while True:
        # Llamar a la función api_call con el path y los parámetros
        result = api_call(path, params)
        
        results.extend(result)  # Agregar los resultados a la lista
        
        # Verificar si la cantidad de resultados es menor que limit
        length_result = len(result)
        print(f"La cantidad de resultados obtenidos es: {length_result}") 
        print()
        if length_result < params["limit"]:
            break
        
        # Actualizar el offset para la siguiente llamada
        params["offset"] += params["limit"]
        
        
    insert_companies(results)
    
    return True