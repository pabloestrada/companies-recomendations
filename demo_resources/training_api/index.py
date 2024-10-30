from flask import Flask, request, jsonify
from dotenv import load_dotenv 
import os
import boto3
import psycopg2
import pandas as pd
import json
import annoy
import tempfile
import numpy as np

# Obtener las variables de entorno o usar valores predeterminados
endpoint_url = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID", "test")  # Credenciales ficticias para Localstack
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "test")  # Credenciales ficticias
aws_region = os.getenv("AWS_REGION", "us-east-1")  # Región predeterminada

# Obtener las variables de entorno o asignar valores predeterminados
db_name = os.getenv("REDSHIFT_DB")
db_user = os.getenv("REDSHIFT_USER")
db_password = os.getenv("REDSHIFT_PASSWORD")
db_host = os.getenv("REDSHIFT_HOST")
db_port = os.getenv("REDSHIFT_PORT", "5439")
schema_name = os.getenv("REDSHIFT_SCHEMA")
    
# Crear el cliente S3 con las credenciales obtenidas desde variables de entorno
s3 = boto3.client(
    's3',
    endpoint_url=endpoint_url,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

app = Flask(__name__)

# Función para cargar el archivo JSON desde S3
def load_vector_data_from_s3(bucket_name, object_name):
    # Obtener el archivo de S3
    response = s3.get_object(Bucket=bucket_name, Key=object_name)
    file_content = response['Body'].read().decode('utf-8')  # Decodificar el contenido a UTF-8

    # Cargar el contenido como JSON
    json_data = json.loads(file_content)

    # Convertir el JSON a DataFrame (si es necesario)
    if 'df_combined' in json_data:
        df = pd.DataFrame(json_data['df_combined'])
        return df, json_data['vector_dimension']  # Devolver el DataFrame y vector_dimension

    return None, None  # Si no se encuentra el contenido esperado, devuelve None

def load_ann_index_from_s3(bucket_name, object_key, vector_dimension):
    # Crear un archivo temporal para almacenar el índice
    with tempfile.NamedTemporaryFile() as temp_file:
        # Descargar el archivo .ann desde S3
        s3.download_file(bucket_name, object_key, temp_file.name)
        
        # Crear el índice Annoy con la dimensión de vector correcta
        index = annoy.AnnoyIndex(vector_dimension, 'angular')
        
        # Cargar el índice desde el archivo temporal
        index.load(temp_file.name)
        
        return index

# Función para cargar el archivo JSON desde S3
def load_json_data_from_s3(bucket_name, object_key):
    # Descargar el archivo JSON desde S3
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    file_content = response['Body'].read().decode('utf-8')  # Leer y decodificar el contenido a UTF-8
    
    # Cargar el contenido como JSON
    json_data = json.loads(file_content)

    vector_dimension = json_data['vector_dimension']
    
    return vector_dimension

# Función para conectarse a la base de datos
def connect_db():
    
    # Registro con print para verificar valores de configuración
    print("Intentando conectar a Redshift con los siguientes parámetros:")


    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        
        # Establecer el esquema por defecto
        with conn.cursor() as cursor:
            cursor.execute(f'SET search_path TO "{schema_name}"')
        
        print("Conexión establecida y esquema configurado correctamente.")
        return conn

    except psycopg2.OperationalError as e:
        print("Error al intentar conectar a la base de datos:", e)
        return None
    
# Función para cargar los datos desde la tabla payments_l0
def load_data_from_db(external_client_id):
        
    conn = connect_db()  # Conectar a la base de datos
    if conn is None:
        raise ConnectionError("No se pudo establecer la conexión con la base de datos.")
    query = """
        SELECT t.payment_at, t.amount, t.external_client_id, c.company_id, c.category_id, c.is_top_biller
        FROM payments_l0 t
        join companies_l0 c on t.company_code = c.company_code
        WHERE is_current = true AND external_client_id = %s;
    """  # Filtrar por external_client_id y los registros que están marcados como 'current'
    
    # Ejecutar la consulta con el external_client_id como parámetro
    df_combined = pd.read_sql(query, conn, params=(external_client_id,))
    conn.close()  # Cerrar la conexión a la base de datos

    return df_combined
    
# Función para recomendar empresas basado en el índice Annoy y el DataFrame cargado
def recomendar_empresas_para_cliente(client_id, num_recommendations=5, df_combined=None, annoy_index=None):
    # Asegurarse de que el DataFrame y el índice Annoy están disponibles
    if df_combined is None or annoy_index is None:
        print("Datos no cargados correctamente.")
        return []
    # Obtener las empresas que ha pagado el cliente
    empresas_cliente = df_combined[df_combined['external_client_id'] == client_id]['company_id'].unique()
    
    if len(empresas_cliente) == 0:
        print(f"El cliente con ID {client_id} no ha realizado pagos.")
        return []
    # Obtener los embeddings de esas empresas desde el índice
    embeddings = []
    for company_id in empresas_cliente:
        try:
            embedding = np.array(annoy_index.get_item_vector(int(company_id)))
            embeddings.append(embedding)
        except KeyError:
            print(f"Empresa con ID {company_id} no encontrada en el índice.")
    
    if len(embeddings) == 0:
        print(f"No se encontraron empresas en el índice para el cliente {client_id}.")
        return []

    # Calcular el embedding promedio del cliente basado en las empresas que pagó
    embedding_cliente = np.mean(embeddings, axis=0)

    # Buscar las empresas más cercanas al embedding del cliente
    recommended_companies = annoy_index.get_nns_by_vector(embedding_cliente, num_recommendations)  # Ajustado para devolver solo las recomendadas

    # Convertir los IDs a enteros estándar de Python (int)
    empresas_cliente = [int(emp) for emp in empresas_cliente]
    recommended_companies = [int(emp) for emp in recommended_companies]

    # Combinar las empresas que ya pagó el cliente con las nuevas recomendaciones
    empresas_finales = empresas_cliente + recommended_companies

    return empresas_finales

# Función para buscar el company_name y company_code de las empresas recomendadas
def get_company_details(company_ids):
    # Verificar si la lista de IDs está vacía
    if not company_ids:
        print("No hay company_ids para consultar.")
        return []

    conn = connect_db()
    cursor = conn.cursor()

    # Print the company_ids for debugging
    print(f"Company IDs to query: {company_ids}")

    # Construye placeholders y crea una consulta dinámica
    placeholders = ', '.join(['%s'] * len(company_ids))
    query = f"""
        SELECT company_id, company_name, company_code
        FROM companies_l0
        WHERE company_id IN ({placeholders});
    """
    
    # Pasa company_ids directamente como lista de parámetros
    cursor.execute(query, company_ids)
    result = cursor.fetchall()

    # Cerrar la conexión
    cursor.close()
    conn.close()

    # Formatear el resultado en un diccionario
    companies = []
    for row in result:
        companies.append({
            "company_id": row[0],
            "company_name": row[1],
            "company_code": row[2]
        })

    return companies
    
# Ruta para procesar el archivo y construir el índice
@app.route('/create_index', methods=['POST'])
def create_index():
    # Obtener el nombre del archivo y el bucket desde la solicitud
    data = request.json
    print(f"data: {data}")
    bucket_name = data['bucket_name']
    object_name = data['object_name']

    # Cargar los datos desde S3
    df_combined, vector_dimension = load_vector_data_from_s3(bucket_name, object_name)
    if df_combined is None:
        return jsonify({"message": "Error al cargar datos desde S3"}), 400
    
    print(df_combined)

    # Crear el índice Annoy
    index = annoy.AnnoyIndex(vector_dimension, 'angular')

    # Agregar los embeddings
# Asegurarse de que company_id es un entero
    for _, row in df_combined.iterrows():
        company_id = int(row['company_id'])  # Convertir a entero si es necesario

        embedding = [
            row['category_id'],
            *row['co_occurrence_vector'],
            row['average_amount'],
            row['average_frequency'],
            int(row['is_top_biller'])
        ]

        index.add_item(company_id, embedding)

    # Construir el índice con 10 árboles
    index.build(10)

    # Crear un archivo temporal para guardar el índice de Annoy
    with tempfile.NamedTemporaryFile() as temp_file:
        index.save(temp_file.name)

        # Subir el archivo temporal a S3
        index_file_key = 'index/payments_index_with_embeddings.ann'
        s3.upload_file(temp_file.name, bucket_name, index_file_key)

    # Devolver respuesta indicando que el índice fue guardado
    return jsonify({"message": "Índice creado y guardado en S3", "index_file": index_file_key})



@app.route('/recommend_companies', methods=['POST'])
def recommend_companies():
    data = request.json
    client_id = data['client_id']
    num_recommendations = data.get('num_recommendations', 5)
    bucket_name = data['bucket_name']
    index_file_key = data['index_file_key']
    json_file_key = data['json_file_key']
    
    # Cargar el archivo JSON con df_combined y vector_dimension
    df_combined = load_data_from_db(client_id)
    print(df_combined.columns)
    # Cargar el índice Annoy desde S3
    vector_dimension = load_json_data_from_s3(bucket_name, json_file_key)
    print(f"vector_dimension: {vector_dimension}")
    annoy_index = load_ann_index_from_s3(bucket_name, index_file_key, vector_dimension)
    
    # Llamar a la función para obtener las recomendaciones
    recomendaciones = recomendar_empresas_para_cliente(client_id, num_recommendations, df_combined, annoy_index)

    # Obtener los detalles de las empresas recomendadas
    company_details = get_company_details(recomendaciones)
    
    return jsonify({
        "client_id": client_id,
        "recommended_companies": company_details
    })

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)