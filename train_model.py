import pandas as pd
import psycopg2
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

def get_connection():
    return psycopg2.connect(
        dbname="retail_inventory",
        user="postgres",
        password="Akshaya@2006",
        host="localhost",
        port="5432"
    )

conn = get_connection()

# Load data from DB
sales = pd.read_sql("SELECT * FROM sales;", conn)
inventory = pd.read_sql("SELECT * FROM inventory;", conn)

conn.close()

# Merge sales & inventory
data = pd.merge(sales, inventory, on=["date", "product_id"])

# Create target column (stockout = 1 if stock_level == 0)
data["stockout"] = data["stock_level"].apply(lambda x: 1 if x == 0 else 0)

# Features
X = data[["quantity", "stock_level"]]
y = data["stockout"]

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save model
joblib.dump(model, "stockout_model.pkl")

print("Model trained and saved successfully!")