import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend to communicate

# Resolve paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'Model', 'best_model_final.keras')

print(f"Loading model from: {MODEL_PATH}")
try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

CLASSES = ['Buildings', 'Forest', 'Mountain', 'Sea', 'Street']

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
        
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
        
    try:
        # Read image
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes))
        
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        # Resize and preprocess
        img_resized = image.resize((224, 224))
        arr = tf.keras.utils.img_to_array(img_resized)
        
        # Use efficientnet preprocess_input
        from tensorflow.keras.applications.efficientnet import preprocess_input
        arr = preprocess_input(arr)
        arr = np.expand_dims(arr, axis=0)
        
        # Predict
        probs = model.predict(arr, verbose=0)[0]
        
        # Format response
        results = [{'class': CLASSES[i], 'probability': float(probs[i])} for i in range(len(CLASSES))]
        
        # Sort results by probability descending
        results = sorted(results, key=lambda x: x['probability'], reverse=True)
        
        return jsonify({
            'success': True,
            'predictions': results,
            'top_class': results[0]['class'],
            'top_probability': results[0]['probability']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
