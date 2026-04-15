from app.models.sale import Sale
from app.models.stock import Stock
from app.models import db
from datetime import datetime

class SalesService:
    @staticmethod
    def record_sale(medicine_id, quantity):
        quantity = int(quantity)
        stock = Stock.query.filter_by(medicine_id=medicine_id).first()
        
        if not stock or stock.quantity < quantity:
            return False, "Insufficient stock"
            
        # Record sale
        sale = Sale(medicine_id=medicine_id, quantity=quantity)
        db.session.add(sale)
        
        # Deduct stock
        stock.quantity -= quantity
        stock.last_updated = datetime.utcnow().date()
        
        db.session.commit()
        return True, "Sale recorded successfully"

    @staticmethod
    def get_sales_trends():
        # Example: sales by medicine
        return db.session.query(db.func.sum(Sale.quantity), Sale.medicine_id)\
            .group_by(Sale.medicine_id).all()
