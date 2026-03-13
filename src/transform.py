import json
import logging
import pandas as pd
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DRIVERS = {
    1: "verstappen",
    4: "norris"
}


def load_json(filename: str) -> list:
    path = Path(f"data/raw/{filename}")
    with open(path, "r") as f:
        return json.load(f)


def save_parquet(df: pd.DataFrame, filename: str):
    df = pd.DataFrame(data)
    columns = [
        "driver_number", "session_key", "lap_number",
        "lap_duration", "duration_sector_1", "duration_sector_2", "duration_sector_3",
        "i1_speed", "i2_speed", "st_speed", "is_pit_out_lap", "date_start"
    ]
    df = df[columns]
    df["date_start"] = pd.to_datetime(df["date_start"], utc=True)
    df["lap_duration"] = pd.to_numeric(df["lap_duration"], errors="coerce")
    df["is_pit_out_lap"] = df["is_pit_out_lap"].fillna(False).astype(bool)
    df = df.dropna(subset=["lap_duration"])

    logging.info(f"{len(df)} voltas transformadas")
    return df


def transform_car_data(data: list) -> pd.DataFrame:
    df = pd.DataFrame(data)
    columns = ["driver_number", "session_key", "date", "speed", "throttle", "brake"]
    df = df[columns]
    df["date"] = pd.to_datetime(df["date"], utc=True)
    df["speed"] = pd.to_numeric(df["speed"], errors="coerce")
    df["throttle"] = pd.to_numeric(df["throttle"], errors="coerce")
    df["brake"] = pd.to_numeric(df["brake"], errors="coerce")
    df = df.dropna(subset=["speed"])

    logging.info(f"{len(df)} registros de telemetria transformados")
    return df


def run():
    drivers_data = load_json("drivers.json")
    df_drivers = transform_drivers(drivers_data)
    save_parquet(df_drivers, "drivers.parquet")
    for driver_number, name in DRIVERS.items():
        laps_data = load_json(f"laps_{name}.json")
        df_laps = transform_laps(laps_data)
        save_parquet(df_laps, f"laps_{name}.parquet")
        car_data = load_json(f"car_data_{name}.json")
        df_car = transform_car_data(car_data)
        save_parquet(df_car, f"car_data_{name}.parquet")


if __name__ == "__main__":
    run()