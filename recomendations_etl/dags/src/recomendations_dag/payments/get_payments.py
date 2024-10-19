import sys
import os

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..

from helpers.api_call.api_call import api_call  # Asegúrate de que la ruta sea correcta

def get_payments(updated_date_to_find=None, limit=1000, offset=0):

    if updated_date_to_find is None:
        raise ValueError("Se debe proporcionar updated_date_to_find.")

    path = "payments"  # El path que deseas consultar
    params = {
        "limit": limit,  # Usar el valor de limit proporcionado
        "offset": offset  # Usar el valor de offset proporcionado
    }
    
    params["updated_at"] = updated_date_to_find
    
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
        
    return results  # Retornar todos los resultados acumulados