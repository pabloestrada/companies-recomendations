import sys
import os
import io 
from dotenv import load_dotenv  # Importar load_dotenv
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
from .get_payments import get_payments

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..

from helpers.bucket.index import put_file_s3  # Asegúrate de que la ruta sea correcta

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def save_payments_to_bucket(updated_date_to_find=None, limit=1000, offset=0, bucket_name=None):
    # Llamar a la función get_payments para obtener los registros
    payment_results = get_payments(updated_date_to_find=updated_date_to_find, limit=limit, offset=offset)

    # Dividir los resultados por la fecha del campo 'updated_at'
    payments_by_date = defaultdict(list)
    for payment in payment_results:
        # Suponiendo que 'updated_at' está en formato 'YYYY-MM-DDTHH:MM:SS'
        updated_at_date = payment['updated_at'].split('T')[0]  # Tomamos solo la parte de la fecha
        payments_by_date[updated_at_date].append(payment)

    # Guardar un archivo por cada fecha en 'payments_by_date' en formato parquet
    files = []

    for date_str, payments in payments_by_date.items():
        # Si hay pagos para la fecha actual, transformamos los datos en un DataFrame y lo guardamos en formato parquet
        if payments:
            df = pd.DataFrame(payments)  # Convertir los pagos en un DataFrame de pandas
            parquet_buffer = io.BytesIO()  # Crear un buffer en memoria
            df.to_parquet(parquet_buffer, index=False)  # Guardar el DataFrame como Parquet en el buffer
            parquet_buffer.seek(0)  # Volver al inicio del buffer
        else:
            continue  # Si no hay pagos, continuar con la siguiente fecha

        # Crear el nombre del archivo con la fecha específica en formato parquet
        file_name = f"{date_str}.parquet"

        # Subir el archivo a S3
        put_file_s3(bucket_name, file_name, parquet_buffer.getvalue())  # Pasar el contenido del buffer
        files.append(file_name)

    return {
        "files": files
    }