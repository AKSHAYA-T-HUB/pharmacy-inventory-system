from app.models import db
from datetime import datetime

class Stock(db.Model):
    __tablename__ = 'stock'
    
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.Date, default=datetime.utcnow().date)

    def to_dict(self):
        return {
            "id": self.id,
            "medicine_id": self.medicine_id,
            "quantity": self.quantity,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }
