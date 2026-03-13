import logging
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DRIVERS = {
    1: "verstappen",
    4: "norris"
}

DB_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


def get_engine():
    engine = create_engine(DB_URL)
    
    logging.info("Conexao com PostgreSQL estabelecida")
    return engine


def load_parquet(filename: str) -> pd.DataFrame:
    path = Path(f"data/transformed/{filename}")
    return pd.read_parquet(path)


def load_to_db(df: pd.DataFrame, table_name: str, engine):
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace", 
        index=False 
    )

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        total = result.scalar()  

    logging.info(f"{len(df)} registros inseridos em '{table_name}' | total na tabela: {total}")


def run():
    engine = get_engine()

    df_drivers = load_parquet("drivers.parquet")
    load_to_db(df_drivers, "drivers", engine)

    for driver_number, name in DRIVERS.items():
        df_laps = load_parquet(f"laps_{name}.parquet")
        load_to_db(df_laps, "laps", engine)
        df_car = load_parquet(f"car_data_{name}.parquet")
        load_to_db(df_car, "car_data", engine)


if __name__ == "__main__":
    run()