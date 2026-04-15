import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

class StockOutPredictor:
    def __init__(self, model_path='app/ml/stockout_model.pkl'):
        self.model_path = model_path
        self.model = None
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)

    def train(self, data_path='inventory.csv'):
        # Improved logic: use more features if available
        # Current app.py uses a very simple X=[[10], [20], [50], [100]], y=[1, 1, 0, 0]
        # Let's build a slightly better mock trainer or use actual data if possible.
        
        # Mocking a better dataset for demonstration
        data = {
            'quantity': [5, 12, 18, 25, 40, 60, 100, 150, 5, 10, 80],
            'daily_sales_avg': [2, 3, 5, 2, 4, 10, 5, 8, 3, 4, 2],
            'lead_time_days': [3, 4, 3, 5, 3, 2, 4, 5, 3, 3, 4],
            'stockout': [1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0]
        }
        df = pd.DataFrame(data)
        
        X = df[['quantity', 'daily_sales_avg', 'lead_time_days']]
        y = df['stockout']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model = RandomForestClassifier(n_estimators=100)
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "report": classification_report(y_test, y_pred, output_dict=True)
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
            
        return metrics

    def predict(self, quantity, daily_sales_avg=5, lead_time_days=3):
        if not self.model:
            return {"error": "Model not trained"}
        
        try:
            # Create a DataFrame to match the training features
            X_input = pd.DataFrame([{
                'quantity': quantity, 
                'daily_sales_avg': daily_sales_avg, 
                'lead_time_days': lead_time_days
            }])
            
            prediction = self.model.predict(X_input)[0]
            probability = self.model.predict_proba(X_input)[0][1]
            
            return {
                "prediction": "High Risk" if prediction == 1 else "Stable",
                "probability": float(probability)
            }
        except Exception as e:
            return {"error": str(e)}
