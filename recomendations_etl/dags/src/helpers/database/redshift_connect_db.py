import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def redshift_connect_db():
    password = os.getenv("REDSHIFT_PASSWORD")
    user = os.getenv("REDSHIFT_USER")
    dbname = os.getenv("REDSHIFT_DB")
    db_host = os.getenv("REDSHIFT_HOST")
    db_port = os.getenv("REDSHIFT_PORT", "5439")
    
    # Registro con print para verificar valores de configuración
    print("Intentando conectar a Redshift con los siguientes parámetros:")
    print(f"Database: {dbname}")
    print(f"User: {user}")
    print(f"Host: {db_host}")
    print(f"Port: {db_port}")

    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=db_host,
            port=db_port
        )
        
        # Establecer el esquema por defecto
        schema_name = os.getenv("REDSHIFT_SCHEMA")
        with conn.cursor() as cursor:
            cursor.execute(f'SET search_path TO "{schema_name}"')
        
        print("Conexión establecida y esquema configurado correctamente.")
        return conn

    except psycopg2.OperationalError as e:
        print("Error al intentar conectar a la base de datos:", e)
        return None