import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode

# Paths INSIDE THE CONTAINER (Linux)
RAW_DIR = "/opt/airflow/data/raw"
BRONZE_DIR = "/opt/airflow/data/bronze"
ETL_LOG_PATH = "/opt/airflow/data/etl_log.json"


def main():
    # Make sure dirs exist
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(BRONZE_DIR, exist_ok=True)

    # Create Spark session
    spark = (
        SparkSession.builder
        .appName("DQ_PySpark_ETL")
        .config("spark.sql.shuffle.partitions", "1")
        .getOrCreate()
    )

    print("Spark Session Created.")

    # ---------- 1) Load RAW JSON from container paths ----------
    orders_path = os.path.join(RAW_DIR, "orders.json")
    products_path = os.path.join(RAW_DIR, "products.json")
    users_path = os.path.join(RAW_DIR, "users.json")

    print(f"Reading RAW files from:\n{orders_path}\n{products_path}\n{users_path}")

    df_orders_raw = spark.read.option("multiLine", True).json(orders_path)
    df_products_raw = spark.read.option("multiLine", True).json(products_path)
    df_users_raw = spark.read.option("multiLine", True).json(users_path)

    print("Raw data loaded successfully.")

    # ---------- 2) BRONZE LAYER TRANSFORMS ----------

    # orders.json (dummyjson carts)
    # Schema: { "carts": [ { id, userId, total, discountedTotal, totalProducts, totalQuantity, products: [...] } ], total, skip, limit }
    bronze_orders = (
        df_orders_raw
        .select(explode("carts").alias("cart"))
        .select(
            col("cart.id").alias("cart_id"),
            col("cart.userId").alias("user_id"),
            col("cart.total").alias("cart_total"),
            col("cart.discountedTotal").alias("cart_discounted_total"),
            col("cart.totalProducts").alias("total_products"),
            col("cart.totalQuantity").alias("total_quantity"),
        )
    )

    # products.json (dummyjson products)
    # Schema: { "products": [ { id,title,description,price,stock,... } ], total, skip, limit }
    bronze_products = (
        df_products_raw
        .select(explode("products").alias("product"))
        .select(
            col("product.id").alias("product_id"),
            col("product.title").alias("title"),
            col("product.description").alias("description"),
            col("product.price").alias("price"),
            col("product.stock").alias("stock"),
        )
    )

    # users.json (dummyjson users)
    # Schema: { "users": [ { id,firstName,lastName,email,age,... } ], total, skip, limit }
    bronze_users = (
        df_users_raw
        .select(explode("users").alias("user"))
        .select(
            col("user.id").alias("user_id"),
            col("user.firstName").alias("first_name"),
            col("user.lastName").alias("last_name"),
            col("user.email").alias("email"),
            col("user.age").alias("age"),
        )
    )

    print("Bronze transforms created:")
    print(f"bronze_orders:  {bronze_orders.count()} rows")
    print(f"bronze_products:{bronze_products.count()} rows")
    print(f"bronze_users:   {bronze_users.count()} rows")

    # ---------- 3) WRITE BRONZE TO DISK ----------
    bronze_orders_dir = os.path.join(BRONZE_DIR, "orders")
    bronze_products_dir = os.path.join(BRONZE_DIR, "products")
    bronze_users_dir = os.path.join(BRONZE_DIR, "users")

    (
        bronze_orders
        .coalesce(1)
        .write
        .mode("overwrite")
        .json(bronze_orders_dir)
    )

    (
        bronze_products
        .coalesce(1)
        .write
        .mode("overwrite")
        .json(bronze_products_dir)
    )

    (
        bronze_users
        .coalesce(1)
        .write
        .mode("overwrite")
        .json(bronze_users_dir)
    )

    print("Bronze JSON files written to:")
    print(bronze_orders_dir)
    print(bronze_products_dir)
    print(bronze_users_dir)

    # ---------- 4) Simple ETL log ----------
    etl_log = {
        "status": "SUCCESS",
        "orders_rows": bronze_orders.count(),
        "products_rows": bronze_products.count(),
        "users_rows": bronze_users.count(),
        "raw_dir": RAW_DIR,
        "bronze_dir": BRONZE_DIR,
    }

    import json
    with open(ETL_LOG_PATH, "w") as f:
        json.dump(etl_log, f, indent=4)

    print(f"ETL log written to {ETL_LOG_PATH}")
    print("Spark ETL completed successfully.")
    spark.stop()


if __name__ == "__main__":
    main()
