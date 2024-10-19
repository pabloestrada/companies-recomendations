from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

from src.recomendations_dag.bucket.verify_bucket import verify_bucket  # Asegúrate de que la ruta sea correcta
from src.recomendations_dag.payments.save_payments_to_bucket import save_payments_to_bucket  # Asegúrate de que la ruta sea correcta
from src.recomendations_dag.payments.get_last_payments_update import get_last_payments_update
from src.recomendations_dag.payments.update_last_payments_update import update_last_payments_update
from src.recomendations_dag.payments.save_payments_to_db import save_payments_to_db

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 15),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

bucket_name = "payments"

def imprimir_mensaje():
    print("¡Hola! Esta es una función que imprime un mensaje en pantalla.")

with DAG('mi_dag_api', default_args=default_args, schedule_interval='@daily') as dag:
    
    verify_bucket_task = PythonOperator(
        task_id='verify_bucket_task',
        python_callable=verify_bucket,
        op_kwargs={
            'bucket_name': bucket_name
        }
    )
    
    get_last_payments_update_task = PythonOperator(
        task_id='get_last_payments_update_task',
        python_callable=get_last_payments_update,
        op_kwargs={

        }
    )
    
    # Paso 1: Llamar a save_payments_to_bucket
    save_payments_to_bucket_task = PythonOperator(
        task_id='save_payments_to_bucket_task',
        python_callable=save_payments_to_bucket,
        op_kwargs={
            'bucket_name': bucket_name,
            'updated_date_to_find': '{{ task_instance.xcom_pull(task_ids="get_last_payments_update_task")["updated_date_to_find"] }}',
        }
    )
    
    update_last_payments_update_task = PythonOperator(
        task_id='update_last_payments_update_task',
        python_callable=update_last_payments_update,
        op_kwargs={
            'proccess_date': '{{ task_instance.xcom_pull(task_ids="get_last_payments_update_task")["proccess_date"] }}',
        }
    )

    # Paso 2: Llamar a otra_funcion
    save_payments_to_db_task = PythonOperator(
        task_id='save_payments_to_db_task',
        python_callable=save_payments_to_db,
        op_kwargs={
            'bucket_name': bucket_name,
            'files': '{{ task_instance.xcom_pull(task_ids="save_payments_to_bucket_task")["files"] }}',
        }
    )

verify_bucket_task >> get_last_payments_update_task >> save_payments_to_bucket_task >> update_last_payments_update_task >> save_payments_to_db_task    
