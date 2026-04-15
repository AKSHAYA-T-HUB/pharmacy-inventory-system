from flask import Blueprint, jsonify
from flask_login import login_required
from app.ml.stockout_predictor import StockOutPredictor
from app.models.stock import Stock

ml_bp = Blueprint('ml', __name__)
predictor = StockOutPredictor()

@ml_bp.route('/predict/<int:medicine_id>')
@login_required
def predict(medicine_id):
    stock = Stock.query.filter_by(medicine_id=medicine_id).first()
    if not stock:
        return jsonify({"error": "No stock data for this medicine"}), 404
    
    # In a real app, daily_sales_avg would be calculated from sales history
    result = predictor.predict(stock.quantity)
    return jsonify(result)

@ml_bp.route('/train')
@login_required
def train_model():
    metrics = predictor.train()
    return jsonify({"message": "Model trained successfully", "metrics": metrics})
