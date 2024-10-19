import sys
import os
from dotenv import load_dotenv  # Importar load_dotenv
import pandas as pd
import pyarrow.parquet as pq
import io
from ast import literal_eval

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..

from helpers.database.payments import insert_payments  # Asegúrate de que la ruta sea correcta

from helpers.bucket.index import get_file_s3  # Asegúrate de que la ruta sea correcta

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Función para consolidar datos de múltiples archivos y guardarlos en la base de datos
def save_payments_to_db(bucket_name, files=[]):
    # Verificar si files está en formato string y convertirlo en lista si es necesario
    if isinstance(files, str):
        files = literal_eval(files)  # Convertir el string a una lista

    # Lista para almacenar todos los DataFrames de los archivos parquet
    all_dataframes = []
    
    for file_name in files:
        print(f"Procesando file_name: {file_name}")
        
        # Obtener el archivo binario desde S3
        file_content = get_file_s3(bucket_name, file_name)
        
        if file_content is not None:
            # Convertir el contenido binario en un buffer para leerlo como Parquet
            parquet_buffer = io.BytesIO(file_content)

            # Usar pyarrow para convertir el archivo Parquet en DataFrame
            table = pq.read_table(parquet_buffer)
            df = table.to_pandas()  # Convertirlo a un DataFrame de pandas

            all_dataframes.append(df)
        else:
            print(f"Error al procesar {file_name}. No se pudo obtener el archivo.")
    
    # Consolidar todos los DataFrames en uno solo
    if all_dataframes:
        consolidated_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Agregar columnas para SCD Tipo 2
        consolidated_df['start_date'] = pd.Timestamp.now()  # Fecha de inicio de validez del registro
        consolidated_df['end_date'] = None  # Fecha de fin de validez (None significa que es el registro actual)
        consolidated_df['is_current'] = True  # Todos los nuevos registros son actuales

        print(f"consolidated_df:")
        print(consolidated_df.head())  # Mostrar los primeros registros para ver si la consolidación funcionó
        insert_payments(consolidated_df)
    else:
        print("No hay DataFrames consolidados para procesar.")
    