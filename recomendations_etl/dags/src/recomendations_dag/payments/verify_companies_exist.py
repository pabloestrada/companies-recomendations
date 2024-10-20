import sys
import os
# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..

from helpers.database.data_updates import get_last_update  # Asegúrate de que la ruta sea correcta


def verify_companies_exist():
    # Llamar a get_last_update para obtener el último resultado
    result = get_last_update('companies')  # Suponemos que get_last_update() devuelve un resultado con 'last_date_update'
    
    # Verificar si el resultado está vacío o es None, y lanzar un error si no se encontró nada
    if not result:
        raise ValueError("No se encontró ningún registro para 'companies' en data_updates.")
    
    # Imprimir el resultado si existe
    print(f"Resultado del update: {result}")
    
    # Devolver True si el resultado es válido
    return True