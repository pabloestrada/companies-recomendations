import sys
import os
from datetime import datetime, timedelta

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..

from helpers.database.data_updates import get_last_update  # Asegúrate de que la ruta sea correcta


def get_last_payments_update():
    # Calcular la fecha actual y la fecha 3 días atrás
    new_last_date_update = datetime.now()  # Mantener como datetime para incluir la hora actual
    updated_date_to_find = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')  # Buscar por actualizaciones desde hace 3 días

    result = get_last_update('payments')  # Suponemos que get_last_update() devuelve un resultado con 'last_date_update'
    print(f"resultado del update {result}")

    # Verificar si el resultado es un array vacío
    if result:
        last_date_update = result[0]['last_date_update']  # Asumiendo que result es una lista de diccionarios

        # Verificar si last_date_update es mayor que la fecha actual (comparación de fechas, no de tiempo)
        if last_date_update > datetime.now().date():
            raise ValueError("No se puede procesar fechas futuras.")

        # Si last_date_update no es igual a hoy, sumamos un día para updated_date_to_find
        if last_date_update < datetime.now().date():
            updated_date_to_find = (last_date_update + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            updated_date_to_find = last_date_update.strftime('%Y-%m-%d')

    # Devolver el nuevo formato
    return {
        'updated_date_to_find': updated_date_to_find,  # Fecha desde la cual buscar updates
        'proccess_date': new_last_date_update.strftime('%Y-%m-%d'),  # Fecha actual en formato 'YYYY-MM-DD'
    }