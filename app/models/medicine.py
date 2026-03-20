from app.models import db
from datetime import datetime

class Medicine(db.Model):
    __tablename__ = 'medicines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    expiry_date = db.Column(db.Date)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    stocks = db.relationship('Stock', backref='medicine', cascade="all, delete-orphan")
    sales = db.relationship('Sale', backref='medicine', cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "price": self.price
        }
