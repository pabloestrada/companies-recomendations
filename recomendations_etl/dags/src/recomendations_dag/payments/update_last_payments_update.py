import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..

from helpers.database.data_updates import insert_update  # Asegúrate de que la ruta sea correcta


def update_last_payments_update(proccess_date=None):

    print(f"proccess_date para el update {proccess_date}")
    if proccess_date is None:
        raise ValueError("El parámetro 'proccess_date' es obligatorio y no puede ser None.")
    
    result = insert_update("payments", proccess_date);
    print(f"resultado del update {result}")

    return result
    