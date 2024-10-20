from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

from src.companies_dag.companies.save_companies_to_db import save_companies_to_db 

from src.companies_dag.companies.update_last_companies_update import update_last_companies_update 

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 10, 15),
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

with DAG('companies', default_args=default_args, schedule_interval='@weekly', catchup=False) as dag:
    
    # Paso 1: Llamar a save_companies_to_db
    save_companies_to_db_task = PythonOperator(
        task_id='save_companies_to_db_task',
        python_callable=save_companies_to_db,
        op_kwargs={}
    )

    update_last_companies_update_task = PythonOperator(
        task_id='update_last_companies_update_task',
        python_callable=update_last_companies_update,
        op_kwargs={}
    )


save_companies_to_db_task >> update_last_companies_update_task