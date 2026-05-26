import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

EXCEL_FILE = DATA_DIR / "ecommerce_data_final.xlsx"
REPORT_TEMPLATE = TEMPLATE_DIR / "report.html"
REPORT_OUTPUT = OUTPUT_DIR / "final_report.html"

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "Manichandu@30"),
    "database": os.getenv("MYSQL_DATABASE", "ecommerce_project"),
}

TABLE_NAME = os.getenv("MYSQL_TABLE", "orders")

EMAIL_CONFIG = {
    "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "smtp_timeout": int(os.getenv("SMTP_TIMEOUT", "120")),
    "sender": os.getenv("EMAIL_SENDER", ""),
    "receiver": os.getenv("EMAIL_RECEIVER", ""),
    "password": os.getenv("EMAIL_APP_PASSWORD", ""),
}
