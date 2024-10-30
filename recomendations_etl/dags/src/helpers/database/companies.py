from .redshift_connect_db import redshift_connect_db
from psycopg2.extras import execute_values

def insert_companies(companies):
    conn = redshift_connect_db()  # Conectar a la base de datos
    try:
        # Iniciar una transacción
        cursor = conn.cursor()

        # Paso 1: Truncar la tabla
        cursor.execute("TRUNCATE TABLE companies_l0")

        # Paso 2: Crear una lista de tuplas con los valores a insertar
        data = [
            (
                company['id'], 
                company['company_code'], 
                company['company_name'], 
                company.get('category_id'),  # Puede ser None
                company.get('category_name'),  # Puede ser None
                company.get('is_top_biller', False)  # Valor por defecto es False si no está definido
            )
            for company in companies
        ]
        
        # Paso 3: Query de inserción para la tabla `companies_l0`
        insert_query = """
            INSERT INTO companies_l0 (
                company_id, company_code, company_name, category_id, category_name, is_top_biller
            ) VALUES %s
        """

        # Usar `execute_values` para hacer el bulk insert
        execute_values(cursor, insert_query, data)

        # Confirmar la transacción
        conn.commit()
    
    except Exception as e:
        # Hacer rollback si algo falla
        conn.rollback()
        print(f"Error: {e}")
        raise  # Relanzar el error para que pueda ser manejado por el código llamante
    
    finally:
        # Cerrar el cursor y la conexión
        cursor.close()
        conn.close()