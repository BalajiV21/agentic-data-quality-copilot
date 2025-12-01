from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.email import send_email
from datetime import datetime, timedelta
import os
import json

# Import API fetcher
from utils.api_fetcher import fetch_all_data

# Paths inside Airflow container
RAW_DIR = "/opt/airflow/data/raw"
ETL_LOG_PATH = "/opt/airflow/data/etl_log.json"
AGENT_SUMMARY_PATH = "/opt/airflow/data/agent_summary.txt"

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

dag = DAG(
    dag_id="dq_pipeline",
    default_args=default_args,
    description="Data Quality Pipeline with API → PySpark → Agent Analysis",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
)


# ------------------------------
# Task 1: API Fetcher
# ------------------------------
def run_api_fetcher(**context):
    return fetch_all_data()

fetch_api_data = PythonOperator(
    task_id="fetch_api_data",
    python_callable=run_api_fetcher,
    provide_context=True,
    dag=dag,
)


# ------------------------------
# Task 2: Run PySpark ETL inside container
# ------------------------------
def run_spark_pipeline():
    exit_code = os.system("python /opt/airflow/dags/utils/spark_etl.py")
    print(f"Spark ETL exit code = {exit_code}")


spark_etl_task = PythonOperator(
    task_id="spark_etl",
    python_callable=run_spark_pipeline,
    dag=dag,
)


# ------------------------------
# Task 3: Run Agentic AI
# ------------------------------
def run_agent():
    exit_code = os.system("python /opt/airflow/dags/utils/agent_runner.py")
    print(f"Agent exit code = {exit_code}")


run_agent_task = PythonOperator(
    task_id="run_agent",
    python_callable=run_agent,
    dag=dag,
)


# ------------------------------
# Task 4: Send Email Alerts
# ------------------------------
def send_email_if_needed():

    if not os.path.exists(AGENT_SUMMARY_PATH):
        print("Agent summary missing → skipping email.")
        return

    with open(AGENT_SUMMARY_PATH, "r") as f:
        summary = f.read()

    if "ISSUES_FOUND=True" in summary:
        send_email(
            to=["your_email@gmail.com"],
            subject="Data Quality Issue Detected",
            html_content=f"<p>{summary}</p>",
        )
    else:
        print("No issues found → no email sent.")


send_email_task = PythonOperator(
    task_id="send_email",
    python_callable=send_email_if_needed,
    dag=dag,
)


# Task flow
fetch_api_data >> spark_etl_task >> run_agent_task >> send_email_task
