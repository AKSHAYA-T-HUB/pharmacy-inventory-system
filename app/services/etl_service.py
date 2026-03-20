import pandas as pd
from app.models.medicine import Medicine
from app.models.stock import Stock
from app.models.sale import Sale
from app.models import db
import os
from datetime import datetime

class ETLService:
    @staticmethod
    def import_from_csv(inventory_path='inventory.csv', sales_path='sales.csv'):
        """
        Automated ETL to sync CSV data with Database
        """
        if os.path.exists(inventory_path):
            inv_df = pd.read_csv(inventory_path)
            # Logic to upsert data
            for _, row in inv_df.iterrows():
                # This is a simplified example
                # In a real scenario, you'd match by 'name' or a unique code
                pass
        
        return "ETL process completed (Placeholder logic)"

    @staticmethod
    def generate_daily_report():
        """
        Generates analytics report and saves to static folder
        """
        now = datetime.now().strftime("%Y-%m-%d")
        report_path = f'app/static/reports/report_{now}.csv'
        
        if not os.path.exists('app/static/reports'):
            os.makedirs('app/static/reports')
            
        # Summary query
        results = db.session.query(Medicine.name, Stock.quantity)\
            .join(Stock, Medicine.id == Stock.medicine_id).all()
        
        df = pd.DataFrame(results, columns=['Medicine', 'Current Stock'])
        df.to_csv(report_path, index=False)
        
        return report_path
