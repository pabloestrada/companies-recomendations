import sys
import os
from tabulate import tabulate

# Agregar el directorio raíz al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))  # Cambiado a ../../..
from helpers.api_call.api_call import api_call_test_training  # Asegúrate de que la ruta sea correcta
from helpers.database.payments import get_payments_for_recomendations  # Asegúrate de que la ruta sea correcta

def validate_payments_index(bucket_name, index_file_key, json_file_key, payments_from):
    payments = get_payments_for_recomendations(payments_from, 5)
    
    # Recorrer el DataFrame de pagos y hacer llamadas a la API por cada external_client_id
    for index, row in payments.iterrows():
        external_client_id = row['external_client_id']  # Extraer el client_id
        
        # Configurar los parámetros para la llamada a la API
        params = {
            "client_id": external_client_id,  # Usar el client_id extraído
            "num_recommendations": 10,
            "bucket_name": bucket_name,
            "index_file_key": index_file_key,
            "json_file_key": json_file_key 
        }
        
        # Invocar la API para cada registro
        response_training = api_call_test_training(params)
        recommended_companies = response_training.get("recommended_companies", [])
        print_recommendations(external_client_id, recommended_companies)
        
    
    return "Todas las llamadas completadas"


def print_recommendations(external_client_id, recommended_companies):
    print(f"\n\n\nRespuesta para cliente {external_client_id}:")
    # Define the headers for the table
    headers = ["Company ID", "Company Name", "Company Code"]

    # Prepare the data for tabulation
    table_data = [
        [company["company_id"], company["company_name"], company["company_code"]]
        for company in recommended_companies
    ]

    # Print the table using tabulate
    print(tabulate(table_data, headers, tablefmt="grid"))