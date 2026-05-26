# Python MySQL E-Commerce Project

This project imports e-commerce order data from Excel into MySQL, creates a dynamic table, generates HTML sales reports, and can send the generated report through SMTP email.

## Features

- Creates the MySQL database and tables automatically
- Reads order data from `data/ecommerce_data_final.xlsx`
- Inserts or updates order records in MySQL
- Generates an HTML sales report
- Creates customer-specific reports
- Sends the generated report using SMTP
- Creates a MySQL daily summary event

## Setup

1. Install Python 3.13.
2. Install dependencies:

```powershell
py -3.13 -m pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and update the MySQL and SMTP values.
4. Run the project:

```powershell
py -3.13 main.py
```

## Notes

The real `.env` file is ignored by git because it contains private passwords and email app credentials.
