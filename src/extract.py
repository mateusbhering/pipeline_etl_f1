import requests
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://api.openf1.org/v1"

SESSION_KEY = 9839

DRIVERS = {
    1: "verstappen",
    4: "norris"
}


def extract_drivers(session_key: int) -> list:
    response = requests.get(f"{BASE_URL}/drivers", params={"session_key": session_key})
    response.raise_for_status()
    data = response.json()
    logging.info(f"{len(data)} pilotos extraidos")
    return data


def extract_laps(session_key: int, driver_number: int) -> list:
    response = requests.get(f"{BASE_URL}/laps", params={
        "session_key": session_key,
        "driver_number": driver_number
    })
    response.raise_for_status()
    data = response.json()
    logging.info(f"{len(data)} voltas extraidas para o piloto {driver_number}")
    return data


def extract_car_data(session_key: int, driver_number: int) -> list:
    response = requests.get(f"{BASE_URL}/car_data", params={
        "session_key": session_key,
        "driver_number": driver_number
    })
    response.raise_for_status()
    data = response.json()
    logging.info(f"{len(data)} registros de telemetria extraidos para o piloto {driver_number}")
    return data


def save(data: list, filename: str):
    path = Path(f"data/raw/{filename}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    
    logging.info(f"Salvo em {path}")


def run():
    drivers = extract_drivers(SESSION_KEY)
    save(drivers, "drivers.json")
    for driver_number, name in DRIVERS.items():
        laps = extract_laps(SESSION_KEY, driver_number)
        save(laps, f"laps_{name}.json")

        car_data = extract_car_data(SESSION_KEY, driver_number)
        save(car_data, f"car_data_{name}.json")


if __name__ == "__main__":
    run()