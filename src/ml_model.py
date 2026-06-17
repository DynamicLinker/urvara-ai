import pickle
import numpy as np
import os

# Path to the model file
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'crop_recommendation_model.pkl')

def predict_crops(n, p, k, temp, humidity, ph, rainfall):
    """
    Uses the local .pkl model to predict the top 3 crops based on soil and weather data.
    """
    try:
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        
        # Features: N, P, K, temperature, humidity, ph, rainfall
        features = np.array([[n, p, k, temp, humidity, ph, rainfall]])
        
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(features)[0]
            # Get the classes (crop names)
            classes = model.classes_
            
            # Get indices of top 3 probabilities in descending order
            top_3_indices = np.argsort(probabilities)[-3:][::-1]
            top_3_crops = [classes[i] for i in top_3_indices]
            return top_3_crops
        else:
            prediction = model.predict(features)
            return [prediction[0]]
            
    except Exception as e:
        print(f"Model Prediction Error: {e}")
        # Fallback recommendations if model fails
        return ["Rice", "Wheat", "Maize"]
