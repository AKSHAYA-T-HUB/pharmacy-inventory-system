import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

products = [f"P{i}" for i in range(1, 21)]  # 20 products
start_date = datetime(2024, 1, 1)
days = 60

sales_data = []
inventory_data = []

stock = {p: 100 for p in products}

for i in range(days):
    current_date = start_date + timedelta(days=i)
    
    for product in products:
        # Generate random sales
        quantity = np.random.randint(0, 10)
        
        sales_data.append([current_date.date(), product, quantity])
        
        # Update stock
        stock[product] -= quantity
        
        # Restock if low
        if stock[product] < 20:
            stock[product] += 50
        
        inventory_data.append([current_date.date(), product, stock[product]])

sales_df = pd.DataFrame(sales_data, columns=["date", "product_id", "quantity"])
inventory_df = pd.DataFrame(inventory_data, columns=["date", "product_id", "stock_level"])

sales_df.to_csv("sales.csv", index=False)
inventory_df.to_csv("inventory.csv", index=False)

print("CSV files generated successfully!")