import re

import mysql.connector
import pandas as pd

from config.config import DB_CONFIG, EXCEL_FILE, TABLE_NAME


def normalize_column_name(column_name):
    column_name = str(column_name).strip().lower()
    column_name = re.sub(r"[^a-z0-9]+", "_", column_name)
    column_name = column_name.strip("_")
    return column_name or "column"


def mysql_type_for_series(series):
    if pd.api.types.is_integer_dtype(series):
        return "BIGINT"
    if pd.api.types.is_float_dtype(series):
        return "DECIMAL(15, 2)"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "DATETIME"
    return "VARCHAR(255)"


def read_ecommerce_excel():
    df = pd.read_excel(EXCEL_FILE)
    df.columns = [normalize_column_name(column) for column in df.columns]
    return df


def create_table_from_excel():
    df = read_ecommerce_excel()

    column_types = {}
    columns_sql = []
    for column in df.columns:
        mysql_type = mysql_type_for_series(df[column])
        column_types[column] = mysql_type
        if column == "order_id":
            columns_sql.append(f"`{column}` {mysql_type} PRIMARY KEY")
        else:
            columns_sql.append(f"`{column}` {mysql_type}")

    create_sql = f"""
    CREATE TABLE IF NOT EXISTS `{TABLE_NAME}` (
        {", ".join(columns_sql)}
    )
    """

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()
    cursor.execute(create_sql)

    cursor.execute(f"SHOW COLUMNS FROM `{TABLE_NAME}`")
    existing_columns = {row[0] for row in cursor.fetchall()}
    for column, mysql_type in column_types.items():
        if column not in existing_columns:
            cursor.execute(f"ALTER TABLE `{TABLE_NAME}` ADD COLUMN `{column}` {mysql_type}")

    connection.commit()
    cursor.close()
    connection.close()

    print(f"Table ready: {TABLE_NAME}")
    return df.columns.tolist()


if __name__ == "__main__":
    create_table_from_excel()
