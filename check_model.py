import pickle
import os

model_path = 'app/ml/stockout_model.pkl'
if os.path.exists(model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print(f"Model type: {type(model)}")
    try:
        print(f"Number of features: {model.n_features_in_}")
    except AttributeError:
        print("Model doesn't have n_features_in_ attribute.")
else:
    print("Model not found")
