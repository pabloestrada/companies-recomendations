from psycopg2.extras import execute_values
import pandas as pd
from .connect_db import connect_db

def insert_payments(consolidated_df):
    conn = connect_db()  # Conectar a la base de datos
    cursor = conn.cursor()

    # Preparar los datos para el bulk insert
    data_to_insert = []  # Solo insertaremos si se detectan cambios o si es un nuevo registro

    # Paso 1: Consultar y comparar para determinar si el registro ha cambiado
    select_query = """
        SELECT payment_id, payment_at, company_code, status, amount, 
               external_client_id, created_at, updated_at, is_current
        FROM payments_l0
        WHERE payment_id = %s AND company_code = %s AND is_current = TRUE;
    """

    update_query = """
        UPDATE payments_l0
        SET end_date = NOW(), is_current = FALSE
        WHERE payment_id = %s
        AND company_code = %s
        AND is_current = TRUE;
    """

    # Ejecutar el UPDATE para cada fila del dataframe si los datos han cambiado o si es un nuevo registro
    for row in consolidated_df.itertuples(index=False):
        # Consultar el registro actual en la base de datos
        cursor.execute(select_query, (str(row.id), row.company_code))
        existing_row = cursor.fetchone()

        # Si no existe el registro, es un nuevo registro y debemos insertarlo
        if existing_row is None:
            print(f"Inserting new record for payment_id: {row.id}, company_code: {row.company_code}")
            data_to_insert.append((
                row.id, row.payment_at, row.company_code, row.status, 
                row.amount, row.external_client_id, row.created_at, 
                row.updated_at, row.start_date, row.end_date, row.is_current
            ))
        else:
            # Manejar fechas si no son None
            if row.payment_at is not None:
                row_payment_at = pd.to_datetime(row.payment_at).tz_localize(None)
            else:
                row_payment_at = None

            if existing_row[1] is not None:
                existing_payment_at = pd.to_datetime(existing_row[1]).tz_localize(None)
            else:
                existing_payment_at = None

            # Convertir los valores numéricos y de texto a un formato coherente
            row_amount_str = f"{float(row.amount):.2f}"
            existing_amount_str = f"{float(existing_row[4]):.2f}"

            row_status_str = row.status.strip()
            existing_status_str = existing_row[3].strip()

            row_external_client_id_str = row.external_client_id.strip()
            existing_external_client_id_str = existing_row[5].strip()
            # Comparar los valores normalizados
            if (
                row_payment_at != existing_payment_at or
                row_status_str != existing_status_str or
                row_amount_str != existing_amount_str or
                row_external_client_id_str != existing_external_client_id_str
            ):
                # Si algún campo ha cambiado, actualizar el registro anterior
                cursor.execute(update_query, (str(row.id), row.company_code))

                # Agregar el registro a la lista para insertarlo
                data_to_insert.append((
                    row.id, row.payment_at, row.company_code, row.status, 
                    row.amount, row.external_client_id, row.created_at, 
                    row.updated_at, row.start_date, row.end_date, row.is_current
                ))

    # Paso 2: Insertar el nuevo registro solo si hubo actualización o si es un nuevo registro
    if data_to_insert:
        insert_query = """
            INSERT INTO payments_l0 (
                payment_id, payment_at, company_code, status, amount, 
                external_client_id, created_at, updated_at, start_date, end_date, is_current
            ) 
            VALUES %s;
        """

        # Ejecutar el bulk insert usando psycopg2.extras.execute_values
        execute_values(
            cursor, insert_query, data_to_insert, template=None, page_size=1000
        )
        print(f"Inserted {len(data_to_insert)} new records.")
    else:
        print("No new records to insert.")

    conn.commit()
    cursor.close()
    conn.close()