import pandas as pd
import psycopg2

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="retail_inventory",
    user="postgres",
    password="Akshaya@2006",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Load CSV files
sales_df = pd.read_csv("sales.csv")
inventory_df = pd.read_csv("inventory.csv")

# Insert into sales table
for _, row in sales_df.iterrows():
    cur.execute(
        "INSERT INTO sales (date, product_id, quantity) VALUES (%s, %s, %s)",
        (row["date"], row["product_id"], int(row["quantity"]))
    )

# Insert into inventory table
for _, row in inventory_df.iterrows():
    cur.execute(
        "INSERT INTO inventory (date, product_id, stock_level) VALUES (%s, %s, %s)",
        (row["date"], row["product_id"], int(row["stock_level"]))
    )

conn.commit()
cur.close()
conn.close()

print("Data inserted successfully!")