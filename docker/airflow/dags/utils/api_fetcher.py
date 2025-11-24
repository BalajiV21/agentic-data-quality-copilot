import os
import json
import requests
from tenacity import retry, wait_fixed, stop_after_attempt
from datetime import datetime

RAW_DATA_DIR = "/opt/airflow/data/raw"

# Make sure folder exists
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# Retry logic: retry 3 times with 2 seconds wait
@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def fetch_api(url: str):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

def save_json(data: dict, filename: str):
    """Save JSON data to Airflow raw folder"""
    path = os.path.join(RAW_DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    return path

def fetch_all_data():
    """Main function Airflow DAG will call"""

    print("Fetching Orders...")
    orders = fetch_api("https://dummyjson.com/carts")
    orders_path = save_json(orders, "orders.json")

    print("Fetching Products...")
    products = fetch_api("https://dummyjson.com/products")
    products_path = save_json(products, "products.json")

    print("Fetching Users...")
    users = fetch_api("https://dummyjson.com/users")
    users_path = save_json(users, "users.json")

    print("All API data downloaded successfully.")

    return {
        "orders_path": orders_path,
        "products_path": products_path,
        "users_path": users_path,
        "timestamp": datetime.utcnow().isoformat()
    }
if __name__ == "__main__":
    print("Running API Fetcher Test...")
    result = fetch_all_data()
    print(result)
