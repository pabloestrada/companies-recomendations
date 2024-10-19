import psycopg2
from dotenv import load_dotenv 
import os

load_dotenv()

def connect_db():
    
    password = os.getenv("DATA_UPDATED_PASSWORD", "airflow")
    user = os.getenv("DATA_UPDATED_USER", "airflow")
    dbname = os.getenv("DATA_UPDATED_DB", "recomendations_db")
    db_host = os.getenv("DATA_UPDATED_HOST", "postgres")
    
    conn = psycopg2.connect(
        dbname= dbname,
        user= user,
        password= password,
        host=db_host,  # Cambia esto si tu base de datos está en otro host
        port="5432"        # Cambia esto si usas otro puerto
    )
    return conn