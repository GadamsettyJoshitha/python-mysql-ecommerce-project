import logging

import mysql.connector

from config.config import DB_CONFIG, LOG_DIR, TABLE_NAME


LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_DIR / "project.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def create_database():
    server_config = DB_CONFIG.copy()
    database_name = server_config.pop("database")

    connection = mysql.connector.connect(**server_config)
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}`")
    connection.commit()
    cursor.close()
    connection.close()

    logging.info("Database is ready: %s", database_name)
    print(f"Database ready: {database_name}")


def create_mysql_jobs():
    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor()

    try:
        cursor.execute("SET GLOBAL event_scheduler = ON")
    except mysql.connector.Error as error:
        logging.warning("Could not enable event scheduler automatically: %s", error)
        print("Could not enable event scheduler automatically. Enable it in MySQL if needed.")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_sales_summary (
            summary_date DATE PRIMARY KEY,
            total_orders INT NOT NULL,
            total_revenue DECIMAL(15, 2) NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    try:
        cursor.execute("DROP EVENT IF EXISTS daily_ecommerce_summary")
        cursor.execute(
            f"""
            CREATE EVENT daily_ecommerce_summary
            ON SCHEDULE EVERY 1 DAY
            STARTS CURRENT_TIMESTAMP
            DO
            REPLACE INTO daily_sales_summary (summary_date, total_orders, total_revenue)
            SELECT
                CURDATE(),
                COUNT(*),
                COALESCE(SUM(total_amount), 0)
            FROM `{TABLE_NAME}`
            WHERE DATE(order_date) = CURDATE()
            """
        )
        logging.info("MySQL event job is ready: daily_ecommerce_summary")
        print("MySQL job ready: daily_ecommerce_summary")
    except mysql.connector.Error as error:
        logging.warning("Could not create MySQL event job: %s", error)
        print("Could not create MySQL event job. Check EVENT privilege in MySQL.")

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    create_database()
    create_mysql_jobs()
