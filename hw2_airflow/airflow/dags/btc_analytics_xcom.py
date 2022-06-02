import requests
import airflow
import logging

from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator

log = logging.getLogger(__name__)


def _request_data(**context):
    url = 'https://api.coincap.io/v2/rates/bitcoin'
    try:
        req_btc = requests.get(url)
    except requests.ConnectionError as ce:
        log.error(f"Request error: {ce}")

    btc_json = req_btc.json()
    context["task_instance"].xcom_push(key="btc_json", value=btc_json)


def _parse_data(**context):
    btc_json = context["task_instance"].xcom_pull(
            task_ids="request_data", key="btc_json")

    btc_json['timestamp'] = int(btc_json['timestamp'])
    btc_json.update(btc_json['data'])
    del btc_json['data']

    context["task_instance"].xcom_push(key="btc_data", value=btc_json)


def _insert_data(**context):
    btc_data = context["task_instance"].xcom_pull(
        task_ids="parse_data", key="btc_data")
    dest = PostgresHook(postgres_conn_id='ANALYTICS_DB')
    dest_conn = dest.get_conn()
    dest_cursor = dest_conn.cursor()

    dest_cursor.execute(
        '''INSERT INTO btc_data(load_dt, id, symbol, currency_symbol, "type", rate_usd)
           VALUES (
                TO_TIMESTAMP(%(timestamp)s/ 1000),
                %(id)s,
                %(symbol)s,
                %(currencySymbol)s,
                %(type)s,
                %(rateUsd)s
        )''', btc_data)

    dest_conn.commit()


args = {'owner': 'airflow'}

dag = DAG(
    dag_id="btc_analytics_xcom",
    default_args=args,
    description='DAG btc_analytics_xcom - HW2 OTUS-DE',
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval='*/30 * * * *',
    catchup=False,
    tags=['OTUS-DE'],
)

start = DummyOperator(task_id="start", dag=dag)

request_data = PythonOperator(task_id='request_data',
                              python_callable=_request_data,
                              provide_context=True, dag=dag)

parse_data = PythonOperator(task_id='parse_data',
                            python_callable=_parse_data,
                            provide_context=True, dag=dag)

insert_data = PythonOperator(task_id='insert_data',
                             python_callable=_insert_data,
                             provide_context=True, dag=dag)

create_table_if_not_exist = PostgresOperator(
    task_id='create_table_if_not_exist',
    postgres_conn_id="ANALYTICS_DB",
    sql='''CREATE TABLE IF NOT EXISTS btc_data(
            load_dt timestamp NOT NULL,
            id varchar(100) NOT NULL,
            symbol varchar(3) NOT NULL,
            currency_symbol varchar(10) NOT NULL,
            "type" varchar(10) NOT NULL,
            rate_usd decimal NOT NULL
        );''', dag=dag
)

start >> [create_table_if_not_exist, request_data]
request_data >> parse_data
[create_table_if_not_exist, parse_data] >> insert_data
