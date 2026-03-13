from datetime import datetime, timedelta
from airflow.decorators import dag, task
import logging
import subprocess
import os

PROJECT_HOME = os.environ.get("PROJECT_HOME", "/Users/mateus/Desktop/pipeline_formula1")
PYTHON_BIN = os.environ.get("PYTHON_BIN", f"{PROJECT_HOME}/.venv/bin/python")

logger = logging.getLogger("airflow.task")


def run_script(script_path: str) -> int:
    result = subprocess.run(
        [PYTHON_BIN, script_path],
        cwd=PROJECT_HOME,
        capture_output=True,
        text=True
    )
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    return result.returncode


@dag(
    dag_id="f1_etl_pipeline",
    description="Pipeline ETL Fórmula 1: Extract → Transform → Load",
    start_date=datetime(2026, 3, 12),
    schedule_interval="0 10 * * 0",
    catchup=False,
    tags=["f1", "etl", "data", "formula1"],
    default_args={
        "owner": "f1_pipeline",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "execution_timeout": timedelta(minutes=30),
    },
)
def f1_etl_pipeline():
    @task
    def extract_start():
        logger.info("F1 Pipeline: Iniciando EXTRACT (coleta de API)")

    @task
    def extract_data():
        logger.info("📥 Executando: python ./src/extract.py")
        return run_script("./src/extract.py")

    @task
    def extract_end():
        logger.info("F1 Pipeline: EXTRACT concluído com sucesso")

    @task
    def transform_start():
        logger.info("F1 Pipeline: Iniciando TRANSFORM (limpeza e transformação)")

    @task
    def transform_data():
        logger.info("Executando: python ./src/transform.py")
        return run_script("./src/transform.py")

    @task
    def transform_end():
        logger.info("F1 Pipeline: TRANSFORM concluído com sucesso")

    @task
    def load_start():
        logger.info("F1 Pipeline: Iniciando LOAD (ingestão no PostgreSQL)")

    @task
    def load_database():
        logger.info("Executando: python ./src/load.py")
        return run_script("./src/load.py")

    @task
    def load_end():
        logger.info("F1 Pipeline: LOAD concluído com sucesso")

    @task
    def pipeline_success():
        logger.info("Pipeline F1 ETL executado com sucesso!")

    extract_start() >> extract_data() >> extract_end() >> transform_start() >> transform_data() >> transform_end() >> load_start() >> load_database() >> load_end() >> pipeline_success()


f1_etl = f1_etl_pipeline()
