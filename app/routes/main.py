from flask import Blueprint, render_template
from flask_login import login_required
from app.models.medicine import Medicine
from app.models.stock import Stock
from app.models.sale import Sale
from app.models import db
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    # Dashboard metrics
    total_medicines = Medicine.query.count()
    low_stock_count = Stock.query.filter(Stock.quantity < 20).count()
    
    thirty_days_later = datetime.utcnow().date() + timedelta(days=30)
    expiring_soon = Medicine.query.filter(Medicine.expiry_date <= thirty_days_later).count()
    
    total_sales_qty = db.session.query(db.func.sum(Sale.quantity)).scalar() or 0
    
    return render_template('dashboard.html',
                           total_medicines=total_medicines,
                           low_stock=low_stock_count,
                           expiring_soon=expiring_soon,
                           total_sales=total_sales_qty)
