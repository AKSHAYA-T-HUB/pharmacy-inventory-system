from app.models.medicine import Medicine
from app.models.stock import Stock
from app.models import db
from datetime import datetime

class InventoryService:
    @staticmethod
    def get_all_medicines():
        return Medicine.query.all()

    @staticmethod
    def add_medicine(name, category, expiry_date, price):
        new_med = Medicine(name=name, category=category, 
                          expiry_date=datetime.strptime(expiry_date, '%Y-%m-%d').date(), 
                          price=float(price))
        db.session.add(new_med)
        db.session.commit()
        return new_med

    @staticmethod
    def get_stock_data():
        return db.session.query(Medicine.name, Stock.quantity, Stock.last_updated, Medicine.id)\
            .join(Stock, Medicine.id == Stock.medicine_id).all()

    @staticmethod
    def update_stock(medicine_id, quantity):
        stock = Stock.query.filter_by(medicine_id=medicine_id).first()
        if stock:
            stock.quantity += int(quantity)
            stock.last_updated = datetime.utcnow().date()
        else:
            stock = Stock(medicine_id=medicine_id, quantity=int(quantity))
            db.session.add(stock)
        db.session.commit()
        return stock

    @staticmethod
    def delete_medicine(medicine_id):
        medicine = Medicine.query.get(medicine_id)
        if medicine:
            db.session.delete(medicine)
            db.session.commit()
            return True
    @staticmethod
    def export_inventory_csv():
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Medicine Name', 'Quantity', 'Last Updated', 'Medicine ID'])
        
        # Data
        stock_data = InventoryService.get_stock_data()
        for row in stock_data:
            writer.writerow(row)
            
        return output.getvalue()
