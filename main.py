# main.py
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# === Configuration from environment variables ===
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Validate that all required variables are set
if not all([DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME]):
    raise ValueError("Missing database credentials. Please set all environment variables in .env file")

# Create Oracle connection string
conn_str = f'oracle+oracledb://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(conn_str)

print("✅ Connected to Oracle DB")
print("Please paste your SQL query below (must return invoice_date, item_name, invoice_value, etc.):")
print("Type 'exit' to quit.")

# === SQL Execution ===
while True:
    user_query = input("\n>>> ").strip()

    if user_query.lower() in ['exit', 'quit']:
        print("👋 Exiting.")
        break

    try:
        df = pd.read_sql(user_query, con=engine)

        if df.empty:
            print("⚠️ No records returned.")
        else:
            # Ensure the data directory exists
            os.makedirs("data", exist_ok=True)

            # Save to CSV for the dashboard
            output_path = os.path.join("data", "erp_sales_data.csv")
            df.to_csv(output_path, index=False)

            print("✅ Query executed and saved to data/erp_sales_data.csv")
            print(f"💡 Columns: {list(df.columns)}")
    except Exception as e:
        print(f"❌ Error while running query: {e}")