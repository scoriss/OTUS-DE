import requests
import airflow
import logging

from typing import Any, Dict
from datetime import datetime
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.dummy_operator import DummyOperator

log = logging.getLogger(__name__)


def _get_btc_data() -> Dict[str, Any]:
    url = 'https://api.coincap.io/v2/rates/bitcoin'
    try:
        req_btc = requests.get(url)
    except requests.ConnectionError as ce:
        log.error(f"Request error: {ce}")

    btc_json = req_btc.json()

    btc_json['timestamp'] = datetime.utcfromtimestamp(
        int(btc_json['timestamp']) / 1000).replace(microsecond=0)
    btc_json.update(btc_json['data'])
    del btc_json['data']

    return btc_json


args = {'owner': 'airflow'}

dag = DAG(
    dag_id="btc_analytics",
    default_args=args,
    description='DAG btc_analytics - HW2 OTUS-DE',
    start_date=airflow.utils.dates.days_ago(1),
    schedule_interval='*/30 * * * *',
    catchup=False,
    tags=['OTUS-DE'],
)

start = DummyOperator(task_id="start", dag=dag)

insert_btc_data = PostgresOperator(
    task_id='insert_btc_data',
    postgres_conn_id="ANALYTICS_DB",
    sql='''INSERT INTO btc_data(load_dt, id, symbol, currency_symbol, "type", rate_usd)
           VALUES (
                %(timestamp)s,
                %(id)s,
                %(symbol)s,
                %(currencySymbol)s,
                %(type)s,
                %(rateUsd)s
        )''',
    parameters=_get_btc_data()
)

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

start >> create_table_if_not_exist >> insert_btc_data
