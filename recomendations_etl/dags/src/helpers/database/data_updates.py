from psycopg2 import sql
from .connect_db import connect_db

def get_last_update(service_name):
    conn = connect_db()
    cursor = conn.cursor()

    # Modificar la consulta SQL para filtrar por service_name
    cursor.execute("""
        SELECT * FROM data_updates 
        WHERE service_name = %s
        ORDER BY last_date_update DESC 
        LIMIT 1;
    """, (service_name,))  # El valor de service_name se pasa de manera segura con una tupla

    # Usar la función para convertir el registro a un diccionario
    result = records_to_dicts(cursor)

    cursor.close()
    conn.close()
    return result

def insert_update(service_name, last_date_update):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        sql.SQL("""
            INSERT INTO data_updates (service_name, last_date_update)
            VALUES (%s, %s)
            ON CONFLICT (service_name, last_date_update)
            DO UPDATE SET last_date_update = EXCLUDED.last_date_update, updated_at = NOW();
        """),
        [service_name, last_date_update]  # Asegúrate de que last_date_update sea un objeto datetime o un string en formato correcto
    )

    conn.commit()
    cursor.close()
    conn.close()
    
def records_to_dicts(cursor):
    """Convierte todos los registros de un cursor en una lista de diccionarios usando los nombres de las columnas."""
    # Obtener los nombres de las columnas
    columns = [desc[0] for desc in cursor.description]
    
    # Obtener todas las filas
    records = cursor.fetchall()
    
    # Crear una lista de diccionarios
    return [dict(zip(columns, record)) for record in records]  # Crear un diccionario para cada fila
