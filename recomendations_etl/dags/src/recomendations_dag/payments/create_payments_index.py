import sys
import os
import json
import pandas as pd
import requests

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..
from helpers.bucket.index import put_file_s3  # Asegúrate de que la ruta sea correcta
from helpers.api_call.api_call import api_call_training  # Asegúrate de que la ruta sea correcta
from helpers.database.payments import get_payments_for_recomendations  # Asegúrate de que la ruta sea correcta

def create_payments_index(payments_from, bucket_name, payment_index_location):
    data = get_payments_for_recomendations(payments_from)
    print("Datos crudos:", data)
    # Crear un DataFrame a partir de los datos
    df = pd.DataFrame(data)
    print("Columnas del DataFrame:", df.columns)
    print(df.head(20))
    
    df['payment_at'] = pd.to_datetime(df['payment_at'])
    
    # Calcular el monto promedio pagado por empresa
    average_payment_by_company = df.groupby('company_id')['amount'].mean().reset_index()
    average_payment_by_company.columns = ['company_id', 'average_amount']
    
    print("Monto promedio pagado por empresa:")
    print(average_payment_by_company)
    
    # Ordenar por empresa y fecha para calcular la frecuencia de pagos
    df = df.sort_values(by=['company_id', 'payment_at'])
    df['days_since_last_payment'] = df.groupby('company_id')['payment_at'].diff().dt.days

    # Calcular la frecuencia media de pagos por empresa
    payment_frequency_by_company = df.groupby('company_id')['days_since_last_payment'].mean().reset_index().fillna(0)
    payment_frequency_by_company.columns = ['company_id', 'average_frequency']

    print("Frecuencia de pagos por empresa:")
    print(payment_frequency_by_company)

    # Crear la matriz de co-ocurrencias
    co_occurrence_matrix = pd.crosstab(df['external_client_id'], df['company_id'])

    # Calcular la co-ocurrencia entre empresas
    company_co_occurrence = co_occurrence_matrix.T.dot(co_occurrence_matrix)

    # Asegurarse de que la diagonal (co-ocurrencia consigo misma) sea cero
    for company_id in company_co_occurrence.columns:
        company_co_occurrence.loc[company_id, company_id] = 0 

    print("Matriz de co-ocurrencias:")
    print(company_co_occurrence)

    # Combinar la información
    df_combined = pd.merge(average_payment_by_company, payment_frequency_by_company, on='company_id')
    df_combined['category_id'] = df.groupby('company_id')['category_id'].first().reset_index(drop=True)
    df_combined['is_top_biller'] = df.groupby('company_id')['is_top_biller'].first().reset_index(drop=True)
    df_combined['co_occurrence_vector'] = company_co_occurrence.values.tolist()

    # Dimensión del embedding (category_id + co_occurrence_vector + average_amount + average_frequency + is_top_biller)
    vector_dimension = len(df_combined['co_occurrence_vector'][0]) + 4  # 4 es category_id + average_amount + average_frequency + is_top_biller
    print(f"Dimensión del vector utilizado al crear el índice: {vector_dimension}")
    
    
    # Imprimir los primeros 20 registros
    print(df.head(20))
    
    # Crear el objeto a guardar en S3
    # Convertir df_combined a una lista de diccionarios
    df_combined_json = df_combined.to_dict(orient='records')

    # Crear el objeto a guardar en S3 con un DataFrame serializable
    data_to_store = {
        'vector_dimension': vector_dimension,
        'df_combined': df_combined_json
    }


    # Convertir el objeto a JSON
    json_data = json.dumps(data_to_store)
    put_file_s3(bucket_name, payment_index_location, json_data)
    
    params = {
        'bucket_name': bucket_name,
        'object_name': payment_index_location,
        'vector_dimension': vector_dimension
    }
    
    response_training = api_call_training(params)

    return response_training