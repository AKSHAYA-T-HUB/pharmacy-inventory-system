from app.models import db
from datetime import datetime

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    sale_date = db.Column(db.Date, default=datetime.utcnow().date)

    def to_dict(self):
        return {
            "id": self.id,
            "medicine_id": self.medicine_id,
            "quantity": self.quantity,
            "sale_date": self.sale_date.isoformat() if self.sale_date else None
        }
