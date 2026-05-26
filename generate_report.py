from datetime import datetime
import re

import mysql.connector
from jinja2 import Environment, FileSystemLoader, select_autoescape

from config.config import DB_CONFIG, OUTPUT_DIR, REPORT_OUTPUT, TABLE_NAME, TEMPLATE_DIR


def fetch_one(cursor, query, params=None):
    cursor.execute(query, params or ())
    return cursor.fetchone()


def fetch_all(cursor, query, params=None):
    cursor.execute(query, params or ())
    return cursor.fetchall()


def get_template(name):
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )
    return env.get_template(name)


def safe_filename(value):
    value = re.sub(r"[^a-zA-Z0-9._-]+", "_", str(value).strip())
    return value.strip("._") or "customer"


def generate_report():
    OUTPUT_DIR.mkdir(exist_ok=True)

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)

    summary = fetch_one(
        cursor,
        f"""
        SELECT
            COUNT(*) AS total_orders,
            COUNT(DISTINCT customer_id) AS total_customers,
            COALESCE(SUM(total_amount), 0) AS total_revenue,
            COALESCE(AVG(total_amount), 0) AS average_order_value
        FROM `{TABLE_NAME}`
        """,
    )

    category_sales = fetch_all(
        cursor,
        f"""
        SELECT category, COUNT(*) AS orders, COALESCE(SUM(total_amount), 0) AS revenue
        FROM `{TABLE_NAME}`
        GROUP BY category
        ORDER BY revenue DESC
        """,
    )

    status_sales = fetch_all(
        cursor,
        f"""
        SELECT order_status, COUNT(*) AS orders
        FROM `{TABLE_NAME}`
        GROUP BY order_status
        ORDER BY orders DESC
        """,
    )

    recent_orders = fetch_all(
        cursor,
        f"""
        SELECT order_id, customer_id, customer_name, customer_email, order_date,
               product, category, quantity, price, total_amount, payment_method,
               order_status
        FROM `{TABLE_NAME}`
        ORDER BY order_date DESC, order_id DESC
        LIMIT 20
        """,
    )

    cursor.close()
    connection.close()

    template = get_template("report.html")
    html = template.render(
        generated_at=datetime.now().strftime("%d-%m-%Y %I:%M %p"),
        summary=summary,
        category_sales=category_sales,
        status_sales=status_sales,
        recent_orders=recent_orders,
    )

    REPORT_OUTPUT.write_text(html, encoding="utf-8")
    print(f"HTML report generated: {REPORT_OUTPUT}")
    return REPORT_OUTPUT


def generate_customer_report(customer_email):
    customer_report_dir = OUTPUT_DIR / "customer_reports"
    customer_report_dir.mkdir(parents=True, exist_ok=True)

    connection = mysql.connector.connect(**DB_CONFIG)
    cursor = connection.cursor(dictionary=True)

    summary = fetch_one(
        cursor,
        f"""
        SELECT
            customer_id,
            customer_name,
            customer_email,
            COUNT(*) AS total_orders,
            COALESCE(SUM(total_amount), 0) AS total_spent,
            COALESCE(AVG(total_amount), 0) AS average_order_value
        FROM `{TABLE_NAME}`
        WHERE customer_email = %s
        GROUP BY customer_id, customer_name, customer_email
        ORDER BY total_orders DESC
        LIMIT 1
        """,
        (customer_email,),
    )

    orders = fetch_all(
        cursor,
        f"""
        SELECT order_id, order_date, product, category, quantity,
               price, total_amount, payment_method, order_status
        FROM `{TABLE_NAME}`
        WHERE customer_email = %s
        ORDER BY order_date DESC, order_id DESC
        """,
        (customer_email,),
    )

    cursor.close()
    connection.close()

    if not summary:
        return None

    template = get_template("customer_report.html")
    html = template.render(
        generated_at=datetime.now().strftime("%d-%m-%Y %I:%M %p"),
        customer=summary,
        orders=orders,
    )

    report_path = customer_report_dir / f"{safe_filename(customer_email)}_report.html"
    report_path.write_text(html, encoding="utf-8")
    return report_path


if __name__ == "__main__":
    generate_report()
