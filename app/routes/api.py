from flask import Blueprint, jsonify, request
from app.models.medicine import Medicine
from app.models.stock import Stock
from app.models import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/medicines', methods=['GET'])
def get_medicines():
    medicines = Medicine.query.all()
    return jsonify([m.to_dict() for m in medicines])

@api_bp.route('/stock/<int:medicine_id>', methods=['GET'])
def get_stock(medicine_id):
    stock = Stock.query.filter_by(medicine_id=medicine_id).first()
    if stock:
        return jsonify(stock.to_dict())
    return jsonify({"error": "Stock not found"}), 404

@api_bp.route('/analytics/sales-by-medicine', methods=['GET'])
def sales_analytics():
    from app.models.sale import Sale
    results = db.session.query(Medicine.name, db.func.sum(Sale.quantity))\
        .join(Sale, Medicine.id == Sale.medicine_id)\
        .group_by(Medicine.name).all()
    
    return jsonify([{"name": res[0], "value": int(res[1])} for res in results])

@api_bp.route('/analytics/recommendations', methods=['GET'])
def get_recommendations():
    from app.ml.stockout_predictor import StockOutPredictor
    predictor = StockOutPredictor()
    
    # Identify items with low stock (< 30)
    low_stock_items = db.session.query(Medicine, Stock)\
        .join(Stock, Medicine.id == Stock.medicine_id)\
        .filter(Stock.quantity < 30).all()
    
    recommendations = []
    for med, stock in low_stock_items:
        # In this professional version, we use the ML predictor
        pred_result = predictor.predict(stock.quantity)
        recommendations.append({
            "name": med.name,
            "quantity": stock.quantity,
            "prediction": pred_result.get("prediction", "N/A"),
            "probability": f"{int(pred_result.get('probability', 0) * 100)}%",
            "id": med.id
        })
        
    return jsonify(recommendations)
