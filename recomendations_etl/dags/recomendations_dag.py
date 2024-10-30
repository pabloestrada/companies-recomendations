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
from src.recomendations_dag.payments.verify_companies_exist import verify_companies_exist
from src.recomendations_dag.payments.create_payments_index import create_payments_index
from src.recomendations_dag.payments.validate_payments_index import validate_payments_index

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 15),
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'payments_from': datetime.now() - timedelta(days=30),  # Calcula la fecha de hace 30 días
    'bucket_name': 'payments',
    'payment_index_location': 'index/payment_index.json',
    'execution_timeout': timedelta(hours=1)
}


with DAG('recomendations', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:
    
    verify_bucket_task = PythonOperator(
        task_id='verify_bucket_task',
        python_callable=verify_bucket,
        op_kwargs={
            'bucket_name': default_args['bucket_name']
        }
    )
    
    verify_companies_exist_task = PythonOperator(
        task_id='verify_companies_exist_task',
        python_callable=verify_companies_exist,
        op_kwargs={
            'bucket_name': default_args['bucket_name']
        }
    )
    
    get_last_payments_update_task = PythonOperator(
        task_id='get_last_payments_update_task',
        python_callable=get_last_payments_update,
        op_kwargs={}
    )
    
    # Paso 1: Llamar a save_payments_to_bucket
    save_payments_to_bucket_task = PythonOperator(
        task_id='save_payments_to_bucket_task',
        python_callable=save_payments_to_bucket,
        op_kwargs={
            'bucket_name': default_args['bucket_name'],
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
            'bucket_name': default_args['bucket_name'],
            'files': '{{ task_instance.xcom_pull(task_ids="save_payments_to_bucket_task")["files"] }}',
        }
    )
    
    create_payments_index_task = PythonOperator(
        task_id='create_payments_index_task',
        python_callable=create_payments_index,
        op_kwargs={
            'payments_from': default_args['payments_from'],
            'bucket_name': default_args['bucket_name'],
            'payment_index_location': default_args['payment_index_location']
        }
    )
    
    validate_payments_index_task = PythonOperator(
        task_id='validate_payments_index_task',
        python_callable=validate_payments_index,
        op_kwargs={
            'payments_from': default_args['payments_from'],
            'bucket_name': default_args['bucket_name'],
            'index_file_key': '{{ task_instance.xcom_pull(task_ids="create_payments_index_task")["index_file"] }}',
            'json_file_key': default_args['payment_index_location']
        }
    )

verify_bucket_task >> verify_companies_exist_task >> get_last_payments_update_task >> save_payments_to_bucket_task >> update_last_payments_update_task >> save_payments_to_db_task >> create_payments_index_task >> validate_payments_index_task   
