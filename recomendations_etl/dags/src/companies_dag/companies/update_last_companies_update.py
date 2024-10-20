import sys
import os
from datetime import datetime

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..

from helpers.database.data_updates import insert_update  # Asegúrate de que la ruta sea correcta


def update_last_companies_update(proccess_date=datetime.now().date()):

    # Llamar a la función de inserción
    result = insert_update("companies", proccess_date)
    print(f"Resultado del update: {result}")

    return result