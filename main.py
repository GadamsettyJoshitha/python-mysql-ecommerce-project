from create_database import create_database, create_mysql_jobs
from dynamic_insert import insert_excel_data
from dynamic_table import create_table_from_excel
from generate_report import generate_report
from send_email import send_report_email


def main():
    print("Starting E-Commerce Reporting Project...")

    create_database()
    create_table_from_excel()
    inserted_count = insert_excel_data()
    report_path = generate_report()
    create_mysql_jobs()

    print(f"Inserted rows: {inserted_count}")
    print(f"Report generated: {report_path}")

    email_sent = send_report_email(report_path)
    if email_sent:
        print("SMTP report email sent successfully.")
    else:
        print("SMTP email skipped. Check EMAIL_SENDER, EMAIL_RECEIVER, and EMAIL_APP_PASSWORD.")

    print("Project completed successfully.")


if __name__ == "__main__":
    main()
