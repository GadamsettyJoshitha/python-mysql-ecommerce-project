import math

import mysql.connector
import pandas as pd

from config.config import DB_CONFIG, TABLE_NAME
from dynamic_table import read_ecommerce_excel


def clean_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "to_pydatetime"):
        return value.to_pydatetime()
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def insert_excel_data():
    df = read_ecommerce_excel()
    columns = df.columns.tolist()

    column_sql = ", ".join(f"`{column}`" for column in columns)
    placeholders = ", ".join(["%s"] * len(columns))
    update_sql = ", ".join(
        f"`{column}` = VALUES(`{column}`)" for column in columns if column != "order_id"
    )

    insert_sql = f"""
    INSERT INTO `{TABLE_NAME}` ({column_sql})
    VALUES ({placeholders})
    ON DUPLICATE KEY UPDATE {update_sql}
    """

    values = [
        tuple(clean_value(row[column]) for column in columns)
        for _, row in df.iterrows()
    ]

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.executemany(insert_sql, values)
    connection.commit()
    inserted_count = cursor.rowcount
    cursor.close()
    connection.close()

    print(f"Data inserted/updated in {TABLE_NAME}")
    return inserted_count


if __name__ == "__main__":
    insert_excel_data()
