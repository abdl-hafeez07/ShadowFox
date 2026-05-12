import os
import json
import plotly
import plotly.graph_objs as go
from flask import Flask, render_template, request
import pandas as pd
import numpy as np

# Try importing ML libraries
try:
    import joblib
    import xgboost as xgb
    HAS_ML = True
except ImportError:
    HAS_ML = False
    print("Warning: scikit-learn or xgboost or joblib is not installed. Predictions will be mocked.")

app = Flask(__name__)

# Load models and transformers
MODEL_LOADED = False
if HAS_ML:
    try:
        model = joblib.load('best_model/final_xgboost_model.pkl')
        scaler = joblib.load('best_model/final_scaler.pkl')
        encoder = joblib.load('best_model/final_encoder.pkl')
        feature_columns = joblib.load('best_model/final_feature_columns.pkl')
        MODEL_LOADED = True
        print("ML Models loaded successfully!")
    except Exception as e:
        print(f"Error loading models: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/prediction')
def prediction():
    return render_template('prediction.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Retrieve form data
    sales = request.form.get('sales', 0, type=float)
    quantity = request.form.get('quantity', 0, type=int)
    discount = request.form.get('discount', 0, type=float)
    category = request.form.get('category', 'Unknown')
    sub_category = request.form.get('sub_category', 'Unknown')
    state = request.form.get('state', 'Unknown')
    
    prediction_value = 0.0
    recommendation = "No recommendation available."
    chart_json = None

    if not MODEL_LOADED:
        # Fallback if model fails to load or libraries are missing
        print("Using dummy prediction because model is not loaded.")
        prediction_value = 250.75 
        recommendation = "Dummy recommendation for testing."
    else:
        try:
            # Prepare input data DataFrame to match what the model expects
            input_df = pd.DataFrame([[sales, discount, category, sub_category, state, quantity]],
                                    columns=['Sales', 'Discount', 'Category', 'Sub-Category', 'State', 'Quantity'])
            
            # 1. Encode categorical features first
            cat_cols = ['Category', 'Sub-Category', 'State']
            input_df[cat_cols] = encoder.transform(input_df[cat_cols])
            
            # 2. Scale ALL features together
            input_scaled = scaler.transform(input_df)
            
            # 3. Make prediction
            pred = model.predict(input_scaled)
            prediction_value = float(pred[0])
            print(f"Successfully predicted: {prediction_value}")
            
            # --- Generate Dynamic Recommendation ---
            if prediction_value > 0:
                if discount == 0:
                    recommendation = f"Excellent margin. Selling at full price yields maximum profitability for {category}."
                elif discount <= 0.2:
                    recommendation = f"Healthy profit margin despite the {discount*100:.0f}% discount. This level is sustainable and helps drive volume."
                else:
                    recommendation = f"You are profitable, but a high discount of {discount*100:.0f}% is eating into potential revenue. Consider reducing it."
            else:
                if discount > 0:
                    recommendation = f"The {discount*100:.0f}% discount is eroding margins entirely, leading to a loss. AI recommends reducing the discount below 0.20 or bundling items to increase transaction value."
                else:
                    recommendation = f"Even at full price, this combination results in a loss. This indicates high baseline costs or unfavorable dynamics for {sub_category} in {state}."

            chart_json = None

        except Exception as e:
            print(f"Prediction Error: {e}")
            prediction_value = 0.0
            recommendation = "Error generating recommendation."
    
    return render_template('result.html', 
                           prediction=prediction_value,
                           sales=sales,
                           discount=discount,
                           category=category,
                           state=state,
                           recommendation=recommendation,
                           chart_json=chart_json)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
